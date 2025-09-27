import { VerifiedPoC as VerifiedPoCEvent } from "../generated/PoCRegistry/PoCRegistry"
import { VerifiedPoC } from "../generated/schema"

export function handleVerifiedPoC(event: VerifiedPoCEvent): void {
  let entity = new VerifiedPoC(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.pocHash = event.params.pocHash
  entity.target = event.params.target
  entity.attackedVictimBlockNumber = event.params.attackedVictimBlockNumber
  entity.pocType = event.params.pocType
  entity.metadataURI = event.params.metadataURI
  entity.severity = event.params.severity
  entity.summary = event.params.summary

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}
