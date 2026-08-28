"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");

// Mock fabric-shim ClientIdentity module
const mockCidInstance = {
  getMSPID: () => "Org1MSP",
  getAttributeValue: () => "writer",
  getID: () => "x509::/CN=test::/CN=test",
};

require("module").prototype.require = new Proxy(require("module").prototype.require, {
  apply(target, thisArg, argList) {
    if (argList[0] === "fabric-shim") {
      return {
        ClientIdentity: function() {
          return mockCidInstance;
        }
      };
    }
    return Reflect.apply(target, thisArg, argList);
  }
});

const { SpendShieldContract } = require("./index");

// Create fresh mock context for each test
function createMockContext() {
  const state = new Map();
  const events = new Map();
  let txId = "tx-12345";
  let channelId = "spendchannel";

  return {
    stub: {
      getState: async (key) => state.get(key) || Buffer.alloc(0),
      putState: async (key, val) => {
        state.set(key, val);
      },
      getTxID: () => txId,
      getChannelID: () => channelId,
      setEvent: async (name, payload) => {
        events.set(name, payload);
      },
    },
    state,
    events,
    setTxId: (id) => { txId = id; },
  };
}

test("exports the SpendShield contract", () => {
  assert.equal(typeof SpendShieldContract, "function");
});

test("does not expose update operations", () => {
  assert.equal("UpdateEvidence" in SpendShieldContract.prototype, false);
});

test("authorization - authorized MSP can register evidence", async () => {
  const contract = new SpendShieldContract();
  const ctx = createMockContext();

  mockCidInstance.getMSPID = () => "Org1MSP";
  mockCidInstance.getAttributeValue = () => "writer";

  const res = await contract.RegisterEvidence(
    ctx,
    "EV-1",
    "tenant-1",
    "rec-1",
    "INVOICE_REGISTERED",
    "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
    "actor-1",
    "2026-08-28T12:00:00Z",
    "f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5"
  );
  assert.ok(res);
  const parsed = JSON.parse(res);
  assert.equal(parsed.status, "REGISTERED");
  assert.equal(parsed.eventId, "EV-1");
});

test("authorization - unauthorized MSP cannot register evidence", async () => {
  const contract = new SpendShieldContract();
  const ctx = createMockContext();

  mockCidInstance.getMSPID = () => "Org2MSP";

  await assert.rejects(
    contract.RegisterEvidence(
      ctx,
      "EV-1",
      "tenant-1",
      "rec-1",
      "INVOICE_REGISTERED",
      "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
      "actor-1",
      "2026-08-28T12:00:00Z",
      "f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5"
    ),
    /Unauthorized/
  );
});

test("authorization - unauthorized role cannot register evidence", async () => {
  const contract = new SpendShieldContract();
  const ctx = createMockContext();

  mockCidInstance.getMSPID = () => "Org1MSP";
  mockCidInstance.getAttributeValue = () => "reader";

  await assert.rejects(
    contract.RegisterEvidence(
      ctx,
      "EV-1",
      "tenant-1",
      "rec-1",
      "INVOICE_REGISTERED",
      "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
      "actor-1",
      "2026-08-28T12:00:00Z",
      "f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5"
    ),
    /Unauthorized: Role 'writer' or 'admin' required/
  );
});

test("input validation - empty and malformed fields", async () => {
  const contract = new SpendShieldContract();
  const ctx = createMockContext();
  mockCidInstance.getMSPID = () => "Org1MSP";
  mockCidInstance.getAttributeValue = () => "writer";

  // Invalid event ID
  await assert.rejects(
    contract.RegisterEvidence(
      ctx,
      "EV/1",
      "tenant-1",
      "rec-1",
      "INVOICE_REGISTERED",
      "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
      "actor-1",
      "2026-08-28T12:00:00Z",
      "f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5"
    ),
    /Invalid input: eventId contains forbidden characters/
  );

  // Invalid timestamp
  await assert.rejects(
    contract.RegisterEvidence(
      ctx,
      "EV-1",
      "tenant-1",
      "rec-1",
      "INVOICE_REGISTERED",
      "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
      "actor-1",
      "28/08/2026",
      "f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5"
    ),
    /Invalid input: timestamp must be a valid ISO-8601 date string/
  );

  // Invalid document hash
  await assert.rejects(
    contract.RegisterEvidence(
      ctx,
      "EV-1",
      "tenant-1",
      "rec-1",
      "INVOICE_REGISTERED",
      "short-hash",
      "actor-1",
      "2026-08-28T12:00:00Z",
      "f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5"
    ),
    /Invalid input: documentHash must be a SHA-256 hexadecimal value/
  );
});

test("duplicate evidence", async () => {
  const contract = new SpendShieldContract();
  const ctx = createMockContext();
  mockCidInstance.getMSPID = () => "Org1MSP";
  mockCidInstance.getAttributeValue = () => "writer";

  const eventId = "EV-DUP";
  await contract.RegisterEvidence(
    ctx,
    eventId,
    "tenant-1",
    "rec-1",
    "INVOICE_REGISTERED",
    "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
    "actor-1",
    "2026-08-28T12:00:00Z",
    "f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5"
  );

  await assert.rejects(
    contract.RegisterEvidence(
      ctx,
      eventId,
      "tenant-1",
      "rec-1",
      "INVOICE_REGISTERED",
      "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
      "actor-1",
      "2026-08-28T12:00:00Z",
      "f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5"
    ),
    /DUPLICATE_EVENT_ID/
  );
});

test("verification and integrity check", async () => {
  const contract = new SpendShieldContract();
  const ctx = createMockContext();
  mockCidInstance.getMSPID = () => "Org1MSP";
  mockCidInstance.getAttributeValue = () => "writer";

  const hash = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2";
  await contract.RegisterEvidence(
    ctx,
    "EV-VER",
    "tenant-1",
    "rec-1",
    "INVOICE_REGISTERED",
    hash,
    "actor-1",
    "2026-08-28T12:00:00Z",
    "f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5"
  );

  const resVerify = await contract.VerifyEvidence(ctx, "EV-VER", hash);
  const parsedVerify = JSON.parse(resVerify);
  assert.equal(parsedVerify.status, "VERIFIED");

  const resFail = await contract.VerifyEvidence(ctx, "EV-VER", "b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3");
  const parsedFail = JSON.parse(resFail);
  assert.equal(parsedFail.status, "INTEGRITY_FAILURE");
});
