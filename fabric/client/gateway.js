"use strict";

const fs = require("fs");
const crypto = require("crypto");
const readline = require("readline");
const grpc = require("@grpc/grpc-js");
const { connect, signers } = require("@hyperledger/fabric-gateway");

const required = ["FABRIC_CERT_PATH", "FABRIC_KEY_PATH", "FABRIC_TLS_CERT_PATH"];
function config() {
  for (const name of required) if (!process.env[name]) throw new Error(`${name} is required`);
  return {
    channel: process.env.FABRIC_CHANNEL || "spendchannel",
    chaincode: process.env.FABRIC_CHAINCODE || "spendshield",
    endpoint: process.env.FABRIC_PEER_ENDPOINT || "localhost:7051",
    hostAlias: process.env.FABRIC_PEER_HOST_ALIAS || "peer0.org1.example.com",
  };
}
function identity() {
  return { mspId: process.env.FABRIC_MSP_ID || "Org1MSP", credentials: fs.readFileSync(process.env.FABRIC_CERT_PATH) };
}
function signer() {
  const key = crypto.createPrivateKey(fs.readFileSync(process.env.FABRIC_KEY_PATH));
  return signers.newPrivateKeySigner(key);
}
async function withContract(operation) {
  const settings = config();
  const tls = fs.readFileSync(process.env.FABRIC_TLS_CERT_PATH);
  const client = new grpc.Client(settings.endpoint, grpc.credentials.createSsl(tls), { "grpc.ssl_target_name_override": settings.hostAlias });
  const gateway = connect({ client, identity: identity(), signer: signer(), evaluateOptions: () => ({ deadline: Date.now() + 15000 }), endorseOptions: () => ({ deadline: Date.now() + 15000 }), submitOptions: () => ({ deadline: Date.now() + 15000 }) });
  try { return await operation(gateway.getNetwork(settings.channel).getContract(settings.chaincode), settings); }
  finally { gateway.close(); client.close(); }
}
async function main(request) {
  const args = request.arguments || {};
  return withContract(async (contract, settings) => {
    if (request.operation === "registerEvidence") {
      const transaction = contract.newProposal("RegisterEvidence").setArguments(args.eventId, args.tenantId, args.recordId, args.eventType, args.documentHash, args.actor, args.timestamp, args.metadataHash).build();
      const result = await transaction.submit();
      return { ...JSON.parse(Buffer.from(result).toString()), transactionId: transaction.getTransactionId(), channel: settings.channel, chaincode: settings.chaincode };
    }
    const functionName = request.operation === "getEvidence" ? "GetEvidence" : request.operation === "verifyEvidence" ? "VerifyEvidence" : request.operation === "getEvidenceHistory" ? "GetEvidenceHistory" : null;
    if (!functionName) throw new Error("transaction metadata queries require a configured Fabric ledger query implementation");
    const values = request.operation === "verifyEvidence" ? [args.eventId, args.currentDocumentHash] : [args.eventId];
    const result = await contract.evaluateTransaction(functionName, ...values);
    return JSON.parse(Buffer.from(result).toString());
  });
}
const input = readline.createInterface({ input: process.stdin });
input.on("line", async (line) => {
  try { process.stdout.write(`${JSON.stringify(await main(JSON.parse(line)))}\n`); }
  catch (error) { process.stderr.write(`${error.message}\n`); process.exitCode = 1; }
});
