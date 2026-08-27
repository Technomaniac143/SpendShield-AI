"use strict";

const { Contract } = require("fabric-contract-api");
const { ClientIdentity } = require("fabric-shim");

const SUPPORTED_EVENT_TYPES = new Set([
  "INVOICE_REGISTERED", "GRN_REGISTERED", "PAYMENT_APPROVED", "PAYMENT_BLOCKED",
  "DISPUTE_CREATED", "DOCUMENT_VERIFIED", "DOCUMENT_INTEGRITY_FAILED",
  "RECOMMENDATION_ACCEPTED", "RECOMMENDATION_REJECTED", "OUTCOME_RECORDED",
]);
const SHA256 = /^[0-9a-f]{64}$/i;
const ISO_8601 = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$/;
const EVENT_ID_PATTERN = /^[A-Za-z0-9._:-]+$/;
const MAX_STRING_LENGTH = 256;
const MAX_HISTORY_RECORDS = 100;

function stableStringify(obj) {
  if (obj === null) return "null";
  if (typeof obj !== "object") return JSON.stringify(obj);
  if (Array.isArray(obj)) {
    return "[" + obj.map(stableStringify).join(",") + "]";
  }
  const sortedKeys = Object.keys(obj).sort();
  const pairs = sortedKeys.map(k => `${JSON.stringify(k)}:${stableStringify(obj[k])}`);
  return "{" + pairs.join(",") + "}";
}

class SpendShieldContract extends Contract {
  validateAndAuthorize(ctx, requiredRole = null) {
    let cid;
    try {
      cid = new ClientIdentity(ctx.stub);
    } catch (err) {
      throw new Error(`Unauthorized: Client identity could not be verified: ${err.message}`);
    }
    const mspId = cid.getMSPID();
    
    // Access control based on MSP ID
    if (mspId !== "Org1MSP") {
      throw new Error(`Unauthorized: Client from MSP ${mspId} is not permitted to access this resource`);
    }

    // Role-based access control if attributes are set
    const roleAttr = cid.getAttributeValue("role") || cid.getAttributeValue("spendshield.role");
    if (requiredRole && roleAttr) {
      if (roleAttr !== requiredRole && roleAttr !== "admin") {
        throw new Error(`Unauthorized: Role '${requiredRole}' or 'admin' required, but client has role '${roleAttr}'`);
      }
    }
    return { mspId, role: roleAttr, identityId: cid.getID() };
  }

  validateInputs(inputs) {
    const checkStr = (val, name, maxLen = MAX_STRING_LENGTH) => {
      if (typeof val !== "string" || !val.trim()) {
        throw new Error(`Invalid input: ${name} must be a non-empty string`);
      }
      if (val.length > maxLen) {
        throw new Error(`Invalid input: ${name} exceeds maximum length of ${maxLen}`);
      }
    };

    const { eventId, tenantId, recordId, eventType, documentHash, actor, timestamp, metadataHash } = inputs;

    checkStr(eventId, "eventId");
    if (!EVENT_ID_PATTERN.test(eventId)) {
      throw new Error(`Invalid input: eventId contains forbidden characters`);
    }

    checkStr(tenantId, "tenantId");
    if (!EVENT_ID_PATTERN.test(tenantId)) {
      throw new Error(`Invalid input: tenantId contains forbidden characters`);
    }

    checkStr(recordId, "recordId");
    if (!SUPPORTED_EVENT_TYPES.has(eventType)) {
      throw new Error(`Invalid input: unsupported eventType: ${eventType}`);
    }

    checkStr(documentHash, "documentHash");
    if (!SHA256.test(documentHash)) {
      throw new Error(`Invalid input: documentHash must be a SHA-256 hexadecimal value`);
    }

    checkStr(actor, "actor");

    checkStr(timestamp, "timestamp");
    if (!ISO_8601.test(timestamp)) {
      throw new Error(`Invalid input: timestamp must be a valid ISO-8601 date string`);
    }

    if (metadataHash !== undefined && metadataHash !== null) {
      checkStr(metadataHash, "metadataHash");
      if (!SHA256.test(metadataHash)) {
        throw new Error(`Invalid input: metadataHash must be a SHA-256 hexadecimal value`);
      }
    }
  }

  async EvidenceExists(ctx, eventId) {
    if (!eventId || typeof eventId !== "string" || !eventId.trim()) {
      throw new Error("eventId is required");
    }
    const value = await ctx.stub.getState(eventId);
    return value && value.length > 0;
  }

  async RegisterEvidence(ctx, eventId, tenantId, recordId, eventType, documentHash, actor, timestamp, metadataHash) {
    // 1. Authorize Caller
    this.validateAndAuthorize(ctx, "writer");

    // 2. Validate Inputs
    this.validateInputs({ eventId, tenantId, recordId, eventType, documentHash, actor, timestamp, metadataHash });

    // 3. Check for Duplicate
    if (await this.EvidenceExists(ctx, eventId)) {
      throw new Error(`DUPLICATE_EVENT_ID: ${eventId}`);
    }

    const evidence = {
      eventId,
      tenantId,
      recordId,
      eventType,
      documentHash: documentHash.toLowerCase(),
      actor,
      timestamp,
      metadataHash: metadataHash ? metadataHash.toLowerCase() : "",
      fabricTransactionId: ctx.stub.getTxID(),
      chaincodeName: "spendshield",
      channelName: ctx.stub.getChannelID(),
    };

    const serialized = stableStringify(evidence);
    await ctx.stub.putState(eventId, Buffer.from(serialized));

    const payload = stableStringify({
      eventId,
      recordId,
      eventType,
      documentHash: evidence.documentHash,
    });
    await ctx.stub.setEvent("EvidenceRegistered", Buffer.from(payload));

    return JSON.stringify({ status: "REGISTERED", ...evidence });
  }

  async GetEvidence(ctx, eventId) {
    this.validateAndAuthorize(ctx);
    if (!eventId || typeof eventId !== "string" || !eventId.trim()) {
      throw new Error("eventId is required");
    }
    const value = await ctx.stub.getState(eventId);
    if (!value || value.length === 0) {
      return JSON.stringify({ status: "NOT_REGISTERED", eventId });
    }
    return JSON.stringify({ status: "FOUND", ...JSON.parse(value.toString()) });
  }

  async GetEvent(ctx, eventId) {
    return this.GetEvidence(ctx, eventId);
  }

  async VerifyEvidence(ctx, eventId, currentDocumentHash) {
    this.validateAndAuthorize(ctx);
    if (!eventId || typeof eventId !== "string" || !eventId.trim()) {
      throw new Error("eventId is required");
    }
    if (!SHA256.test(currentDocumentHash)) {
      throw new Error("currentDocumentHash must be a SHA-256 hexadecimal value");
    }
    const value = await ctx.stub.getState(eventId);
    if (!value || value.length === 0) {
      return JSON.stringify({ status: "NOT_REGISTERED", eventId });
    }
    const registeredHash = JSON.parse(value.toString()).documentHash;
    const isVerified = registeredHash === currentDocumentHash.toLowerCase();
    return JSON.stringify({
      status: isVerified ? "VERIFIED" : "INTEGRITY_FAILURE",
      eventId,
      registeredHash,
      currentHash: currentDocumentHash.toLowerCase(),
    });
  }

  async GetEvidenceHistory(ctx, eventId) {
    this.validateAndAuthorize(ctx);
    if (!eventId || typeof eventId !== "string" || !eventId.trim()) {
      throw new Error("eventId is required");
    }
    const iterator = await ctx.stub.getHistoryForKey(eventId);
    const history = [];
    try {
      let count = 0;
      while (count < MAX_HISTORY_RECORDS) {
        const item = await iterator.next();
        if (!item.value) {
          if (item.done) break;
          continue;
        }

        let parsedValue = null;
        if (!item.value.isDelete && item.value.value) {
          try {
            parsedValue = JSON.parse(item.value.value.toString());
          } catch (e) {
            parsedValue = { parseError: e.message, rawValue: item.value.value.toString() };
          }
        }

        history.push({
          txId: item.value.txId,
          timestamp: item.value.timestamp,
          isDelete: item.value.isDelete,
          value: parsedValue,
        });

        if (item.done) break;
        count++;
      }
    } finally {
      await iterator.close();
    }
    return JSON.stringify(history);
  }
}

module.exports = { SpendShieldContract };
