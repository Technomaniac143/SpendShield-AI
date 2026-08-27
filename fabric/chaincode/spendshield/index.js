"use strict";

const { Contract } = require("fabric-contract-api");

const SUPPORTED_EVENT_TYPES = new Set([
  "INVOICE_REGISTERED", "GRN_REGISTERED", "PAYMENT_APPROVED", "PAYMENT_BLOCKED",
  "DISPUTE_CREATED", "DOCUMENT_VERIFIED", "DOCUMENT_INTEGRITY_FAILED",
  "RECOMMENDATION_ACCEPTED", "RECOMMENDATION_REJECTED", "OUTCOME_RECORDED",
]);
const SHA256 = /^[0-9a-f]{64}$/i;

class SpendShieldContract extends Contract {
  async EvidenceExists(ctx, eventId) {
    const value = await ctx.stub.getState(eventId);
    return value && value.length > 0;
  }

  async RegisterEvidence(ctx, eventId, tenantId, recordId, eventType, documentHash, actor, timestamp, metadataHash) {
    for (const [name, value] of Object.entries({ eventId, tenantId, recordId, eventType, documentHash, actor, timestamp, metadataHash })) {
      if (!value || !String(value).trim()) throw new Error(`${name} is required`);
    }
    if (!SUPPORTED_EVENT_TYPES.has(eventType)) throw new Error(`unsupported eventType: ${eventType}`);
    if (!SHA256.test(documentHash) || !SHA256.test(metadataHash)) throw new Error("hashes must be SHA-256 hexadecimal values");
    if (await this.EvidenceExists(ctx, eventId)) throw new Error(`DUPLICATE_EVENT_ID: ${eventId}`);

    const evidence = {
      eventId, tenantId, recordId, eventType, documentHash: documentHash.toLowerCase(), actor,
      timestamp, metadataHash: metadataHash.toLowerCase(), fabricTransactionId: ctx.stub.getTxID(),
      chaincodeName: "spendshield", channelName: ctx.stub.getChannelID(),
    };
    await ctx.stub.putState(eventId, Buffer.from(JSON.stringify(evidence)));
    const payload = Buffer.from(JSON.stringify({ eventId, recordId, eventType, documentHash: evidence.documentHash }));
    await ctx.stub.setEvent("EvidenceRegistered", payload);
    return JSON.stringify({ status: "REGISTERED", ...evidence });
  }

  async GetEvidence(ctx, eventId) {
    const value = await ctx.stub.getState(eventId);
    if (!value || value.length === 0) return JSON.stringify({ status: "NOT_REGISTERED", eventId });
    return JSON.stringify({ status: "FOUND", ...JSON.parse(value.toString()) });
  }

  async GetEvent(ctx, eventId) { return this.GetEvidence(ctx, eventId); }

  async VerifyEvidence(ctx, eventId, currentDocumentHash) {
    if (!SHA256.test(currentDocumentHash)) throw new Error("currentDocumentHash must be a SHA-256 hexadecimal value");
    const value = await ctx.stub.getState(eventId);
    if (!value || value.length === 0) return JSON.stringify({ status: "NOT_REGISTERED", eventId });
    const registeredHash = JSON.parse(value.toString()).documentHash;
    return JSON.stringify({ status: registeredHash === currentDocumentHash.toLowerCase() ? "VERIFIED" : "INTEGRITY_FAILURE", eventId, registeredHash, currentHash: currentDocumentHash.toLowerCase() });
  }

  async GetEvidenceHistory(ctx, eventId) {
    const iterator = await ctx.stub.getHistoryForKey(eventId);
    const history = [];
    try {
      while (true) {
        const item = await iterator.next();
        if (item.value && item.value.value) {
          history.push({ txId: item.value.txId, timestamp: item.value.timestamp, isDelete: item.value.isDelete, value: item.value.isDelete ? null : JSON.parse(item.value.value.toString()) });
        }
        if (item.done) break;
      }
    } finally { await iterator.close(); }
    return JSON.stringify(history);
  }
}

module.exports = { SpendShieldContract };
