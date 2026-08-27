"use strict";

const fs = require("fs");
const crypto = require("crypto");
const readline = require("readline");
const grpc = require("@grpc/grpc-js");
const { connect, signers } = require("@hyperledger/fabric-gateway");
const { common } = require("@hyperledger/fabric-protos");

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
function createGateway(settings) {
  const tls = fs.readFileSync(process.env.FABRIC_TLS_CERT_PATH);
  const client = new grpc.Client(settings.endpoint, grpc.credentials.createSsl(tls), { "grpc.ssl_target_name_override": settings.hostAlias });
  const identity = { mspId: process.env.FABRIC_MSP_ID || "Org1MSP", credentials: fs.readFileSync(process.env.FABRIC_CERT_PATH) };
  const key = crypto.createPrivateKey(fs.readFileSync(process.env.FABRIC_KEY_PATH));
  const gateway = connect({ client, identity, signer: signers.newPrivateKeySigner(key), evaluateOptions: () => ({ deadline: Date.now() + 15000 }), endorseOptions: () => ({ deadline: Date.now() + 15000 }), submitOptions: () => ({ deadline: Date.now() + 15000 }), commitStatusOptions: () => ({ deadline: Date.now() + 15000 }) });
  const network = gateway.getNetwork(settings.channel);
  return { client, gateway, network, contract: network.getContract(settings.chaincode) };
}
function errorResponse(error) {
  const message = error?.details?.[0]?.message || error.message || String(error);
  const code = message.startsWith("DUPLICATE_EVENT_ID:") ? "DUPLICATE_EVENT_ID" : "FABRIC_REQUEST_FAILED";
  return { error: { code, message } };
}
async function handle(request, context) {
  const args = request.arguments || {};
  if (request.operation === "registerEvidence") {
    const transaction = context.contract.newProposal("RegisterEvidence").setArguments(args.eventId, args.tenantId, args.recordId, args.eventType, args.documentHash, args.actor, args.timestamp, args.metadataHash).build();
    const result = await transaction.submit();
    return { ...JSON.parse(Buffer.from(result).toString()), transactionId: transaction.getTransactionId(), channel: context.settings.channel, chaincode: context.settings.chaincode };
  }
  if (request.operation === "getTransaction") {
    const block = await context.network.getBlockByTransactionId(args.transactionId);
    const validationCodes = block.metadata?.metadata?.[2] || Buffer.alloc(0);
    let transactionIndex = -1;
    let timestamp = null;
    for (let index = 0; index < (block.data?.data || []).length; index += 1) {
      const envelope = common.Envelope.decode(block.data.data[index]);
      const payload = common.Payload.decode(envelope.payload);
      const header = common.ChannelHeader.decode(payload.header.channel_header);
      if (header.tx_id === args.transactionId) {
        transactionIndex = index;
        if (header.timestamp) timestamp = new Date(Number(header.timestamp.seconds) * 1000 + Math.floor(header.timestamp.nanos / 1000000)).toISOString();
        break;
      }
    }
    return { transactionId: args.transactionId, blockNumber: Number(block.header.number), blockHash: crypto.createHash("sha256").update(common.BlockHeader.encode(block.header).finish()).digest("hex"), timestamp, validationCode: transactionIndex >= 0 ? validationCodes[transactionIndex] : null, channel: context.settings.channel, chaincode: context.settings.chaincode };
  }
  const functionName = request.operation === "getEvidence" ? "GetEvidence" : request.operation === "verifyEvidence" ? "VerifyEvidence" : request.operation === "getEvidenceHistory" ? "GetEvidenceHistory" : null;
  if (!functionName) throw new Error(`unsupported operation: ${request.operation}`);
  const values = request.operation === "verifyEvidence" ? [args.eventId, args.currentDocumentHash] : [args.eventId];
  const result = await context.contract.evaluateTransaction(functionName, ...values);
  const parsed = JSON.parse(Buffer.from(result).toString());
  return request.operation === "getEvidenceHistory" ? { eventId: args.eventId, history: parsed } : parsed;
}
const settings = config();
const context = { ...createGateway(settings), settings };
const input = readline.createInterface({ input: process.stdin });
let queue = Promise.resolve();
input.on("line", (line) => {
  queue = queue.then(async () => {
    try { process.stdout.write(`${JSON.stringify(await handle(JSON.parse(line), context))}\n`); }
    catch (error) { process.stdout.write(`${JSON.stringify(errorResponse(error))}\n`); }
  });
});
input.on("close", async () => { context.gateway.close(); context.client.close(); });
