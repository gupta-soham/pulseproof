import { Graph } from '@graphprotocol/grc-20';

interface VerifiedPocEvent {
  id: string;
  pocId: string;
  contractAddress: string;
  transactionHash: string;
  blockNumber: bigint;
  vulnerabilityType: string;
  severity: string;
  riskScore: number;
  estimatedImpact: number;
  verified: boolean;
  verifiedAt: bigint;
  gasUsed?: bigint;
  executionTime: bigint;
  foundryTestCode: string;
  description: string;
  hederaHash?: string;
  createdAt: bigint;
  updatedAt: bigint;
}

// Create properties for VerifiedPoc
const properties = {
  pocId: Graph.createProperty({ name: 'POC ID', dataType: 'STRING' }),
  contractAddress: Graph.createProperty({ name: 'Contract Address', dataType: 'STRING' }),
  transactionHash: Graph.createProperty({ name: 'Transaction Hash', dataType: 'STRING' }),
  blockNumber: Graph.createProperty({ name: 'Block Number', dataType: 'NUMBER' }),
  vulnerabilityType: Graph.createProperty({ name: 'Vulnerability Type', dataType: 'STRING' }),
  severity: Graph.createProperty({ name: 'Severity', dataType: 'STRING' }),
  riskScore: Graph.createProperty({ name: 'Risk Score', dataType: 'NUMBER' }),
  estimatedImpact: Graph.createProperty({ name: 'Estimated Impact', dataType: 'NUMBER' }),
  verified: Graph.createProperty({ name: 'Verified', dataType: 'BOOLEAN' }),
  verifiedAt: Graph.createProperty({ name: 'Verified At', dataType: 'TIME' }),
  gasUsed: Graph.createProperty({ name: 'Gas Used', dataType: 'NUMBER' }),
  executionTime: Graph.createProperty({ name: 'Execution Time', dataType: 'NUMBER' }),
  foundryTestCode: Graph.createProperty({ name: 'Foundry Test Code', dataType: 'STRING' }),
  description: Graph.createProperty({ name: 'Description', dataType: 'STRING' }),
  hederaHash: Graph.createProperty({ name: 'Hedera Hash', dataType: 'STRING' }),
  createdAt: Graph.createProperty({ name: 'Created At', dataType: 'TIME' }),
  updatedAt: Graph.createProperty({ name: 'Updated At', dataType: 'TIME' })
};

// Create VerifiedPoc type
const { id: verifiedPocTypeId } = Graph.createType({
  name: 'VerifiedPoc',
  properties: Object.values(properties).map(p => p.id)
});

export async function handleVerifiedPocEvent(event: VerifiedPocEvent): Promise<{ ops: any[], entityId: string }> {
  try {
    const { ops: createEntityOps, id: entityId } = Graph.createEntity({
      name: `VerifiedPoc-${event.pocId}`,
      description: event.description,
      types: [verifiedPocTypeId],
      values: [
        { property: properties.pocId.id, value: event.pocId },
        { property: properties.contractAddress.id, value: event.contractAddress },
        { property: properties.transactionHash.id, value: event.transactionHash },
        { property: properties.blockNumber.id, value: Graph.serializeNumber(Number(event.blockNumber)) },
        { property: properties.vulnerabilityType.id, value: event.vulnerabilityType },
        { property: properties.severity.id, value: event.severity },
        { property: properties.riskScore.id, value: Graph.serializeNumber(event.riskScore) },
        { property: properties.estimatedImpact.id, value: Graph.serializeNumber(event.estimatedImpact) },
        { property: properties.verified.id, value: Graph.serializeBoolean(event.verified) },
        { property: properties.verifiedAt.id, value: Graph.serializeDate(new Date(Number(event.verifiedAt) * 1000)) },
        { property: properties.executionTime.id, value: Graph.serializeNumber(Number(event.executionTime)) },
        { property: properties.foundryTestCode.id, value: event.foundryTestCode },
        { property: properties.description.id, value: event.description },
        { property: properties.createdAt.id, value: Graph.serializeDate(new Date(Number(event.createdAt) * 1000)) },
        { property: properties.updatedAt.id, value: Graph.serializeDate(new Date(Number(event.updatedAt) * 1000)) },
        ...(event.gasUsed ? [{ property: properties.gasUsed.id, value: Graph.serializeNumber(Number(event.gasUsed)) }] : []),
        ...(event.hederaHash ? [{ property: properties.hederaHash.id, value: event.hederaHash }] : [])
      ]
    });

    // Return the operations instead of executing them
    // These operations can later be collected and published to IPFS or executed in batch
    console.log(`Created VerifiedPoc entity operations for POC ID: ${event.pocId}`);
    return { ops: createEntityOps, entityId };
  } catch (error) {
    console.error('Error handling VerifiedPoc event:', error);
    throw error;
  }
}