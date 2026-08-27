"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const { SpendShieldContract } = require("./index");

test("exports the SpendShield contract", () => assert.equal(typeof SpendShieldContract, "function"));
test("does not expose update operations", () => assert.equal("UpdateEvidence" in SpendShieldContract.prototype, false));
