"use strict";

const fs = require("fs");
const crypto = require("crypto");
const readline = require("readline");
const grpc = require("@grpc/grpc-js");
const { connect, signers } = require("@hyperledger/fabric-gateway");
const { common } = require("@hyperledger/fabric-protos");

const required = [
  "FABRIC_CERT_PATH",
  "FABRIC_KEY_PATH",
  "FABRIC_TLS_CERT_PATH",
  "FABRIC_GATEWAY_URL",
  "FABRIC_CHANNEL",
  "FABRIC_CHAINCODE",
  "FABRIC_PEER_ENDPOINT",
  "FABRIC_PEER_HOST_ALIAS",
  "FABRIC_MSP_ID"
];

function config() {
  const missing = [];
  for (const name of required) {
    if (!process.env[name]) {
      missing.push(name);
    }
  }
  if (missing.length > 0) {
    throw new Error(`Fabric Configuration Error: Missing required environment variables: ${missing.join(", ")}`);
  }

  // Verify paths exist on startup
  const pathsToVerify = {
    FABRIC_CERT_PATH: process.env.FABRIC_CERT_PATH,
    FABRIC_KEY_PATH: process.env.FABRIC_KEY_PATH,
    FABRIC_TLS_CERT_PATH: process.env.FABRIC_TLS_CERT_PATH
  };

  for (const [key, filePath] of Object.entries(pathsToVerify)) {
    if (!fs.existsSync(filePath)) {
      throw new Error(`Fabric Path Error: File not found for ${key}: '${filePath}'`);
    }
  }

  return {
    channel: process.env.FABRIC_CHANNEL,
    chaincode: process.env.FABRIC_CHAINCODE,
    endpoint: process.env.FABRIC_PEER_ENDPOINT,
    hostAlias: process.env.FABRIC_PEER_HOST_ALIAS,
  };
}

function createGateway(settings) {
  const tls = fs.readFileSync(process.env.FABRIC_TLS_CERT_PATH);
  const client = new grpc.Client(settings.endpoint, grpc.credentials.createSsl(tls), { "grpc.ssl_target_name_override": settings.hostAlias });
  const identity = { mspId: process.env.FABRIC_MSP_ID, credentials: fs.readFileSync(process.env.FABRIC_CERT_PATH) };
  const key = crypto.createPrivateKey(fs.readFileSync(process.env.FABRIC_KEY_PATH));
  const gateway = connect({
    client,
    identity,
    signer: signers.newPrivateKeySigner(key),
    evaluateOptions: () => ({ deadline: Date.now() + 15000 }),
    endorseOptions: () => ({ deadline: Date.now() + 15000 }),
    submitOptions: () => ({ deadline: Date.now() + 15000 }),
    commitStatusOptions: () => ({ deadline: Date.now() + 15000 })
  });
  const network = gateway.getNetwork(settings.channel);
  return { client, gateway, network, contract: network.getContract(settings.chaincode) };
}

function errorResponse(error) {
  const message = error?.details?.[0]?.message || error.message || String(error);
  let code = "FABRIC_REQUEST_FAILED";
  if (message.includes("DUPLICATE_EVENT_ID")) {
    code = "DUPLICATE_EVENT_ID";
  } else if (message.includes("Unauthorized") || message.includes("access denied")) {
    code = "UNAUTHORIZED";
  } else if (message.includes("Invalid input")) {
    code = "INVALID_INPUT";
  }
  return { error: { code, message } };
}

async function handle(request, context) {
  const args = request.arguments || {};
  if (request.operation === "registerEvidence") {
    const transaction = context.contract.newProposal("RegisterEvidence")
      .setArguments(
        args.eventId || "",
        args.tenantId || "",
        args.recordId || "",
        args.eventType || "",
        args.documentHash || "",
        args.actor || "",
        args.timestamp || "",
        args.metadataHash || ""
      ).build();
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
        if (header.timestamp) {
          timestamp = new Date(Number(header.timestamp.seconds) * 1000 + Math.floor(header.timestamp.nanos / 1000000)).toISOString();
        }
        break;
      }
    }

    let status = "UNKNOWN";
    let validationCode = null;
    if (transactionIndex >= 0 && transactionIndex < validationCodes.length) {
      validationCode = validationCodes[transactionIndex];
      status = validationCode === 0 ? "VALID" : "INVALID";
    } else if (transactionIndex >= 0) {
      status = "UNAVAILABLE";
    } else {
      status = "NOT_FOUND";
    }

    return {
      transactionId: args.transactionId,
      blockNumber: Number(block.header.number),
      blockHash: crypto.createHash("sha256").update(common.BlockHeader.encode(block.header).finish()).digest("hex"),
      timestamp,
      validationCode,
      status,
      channel: context.settings.channel,
      chaincode: context.settings.chaincode
    };
  }
  const functionName = request.operation === "getEvidence" ? "GetEvidence" : request.operation === "verifyEvidence" ? "VerifyEvidence" : request.operation === "getEvidenceHistory" ? "GetEvidenceHistory" : null;
  if (!functionName) {
    throw new Error(`unsupported operation: ${request.operation}`);
  }
  const values = request.operation === "verifyEvidence" ? [args.eventId, args.currentDocumentHash] : [args.eventId];
  const result = await context.contract.evaluateTransaction(functionName, ...values);
  const parsed = JSON.parse(Buffer.from(result).toString());
  return request.operation === "getEvidenceHistory" ? { eventId: args.eventId, history: parsed } : parsed;
}

let settings;
let context;
try {
  settings = config();
  context = { ...createGateway(settings), settings };
} catch (err) {
  process.stderr.write(`${err.message}\n`);
  process.exit(1);
}

const input = readline.createInterface({ input: process.stdin });
let queue = Promise.resolve();
input.on("line", (line) => {
  queue = queue.then(async () => {
    try {
      process.stdout.write(`${JSON.stringify(await handle(JSON.parse(line), context))}\n`);
    } catch (error) {
      process.stdout.write(`${JSON.stringify(errorResponse(error))}\n`);
    }
  });
});
input.on("close", async () => {
  if (context) {
    context.gateway.close();
    context.client.close();
  }
});
