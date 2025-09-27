import { newMockEvent } from "matchstick-as"
import { ethereum, Bytes, Address } from "@graphprotocol/graph-ts"
import { VerifiedPoC } from "../generated/PoCRegistry/PoCRegistry"

export function createVerifiedPoCEvent(
  pocHash: Bytes,
  target: Address,
  attackedVictimBlockNumber: i32,
  pocType: string,
  metadataURI: string,
  severity: string,
  summary: string
): VerifiedPoC {
  let verifiedPoCEvent = changetype<VerifiedPoC>(newMockEvent())

  verifiedPoCEvent.parameters = new Array()

  verifiedPoCEvent.parameters.push(
    new ethereum.EventParam("pocHash", ethereum.Value.fromFixedBytes(pocHash))
  )
  verifiedPoCEvent.parameters.push(
    new ethereum.EventParam("target", ethereum.Value.fromAddress(target))
  )
  verifiedPoCEvent.parameters.push(
    new ethereum.EventParam(
      "attackedVictimBlockNumber",
      ethereum.Value.fromUnsignedBigInt(
        BigInt.fromI32(attackedVictimBlockNumber)
      )
    )
  )
  verifiedPoCEvent.parameters.push(
    new ethereum.EventParam("pocType", ethereum.Value.fromString(pocType))
  )
  verifiedPoCEvent.parameters.push(
    new ethereum.EventParam(
      "metadataURI",
      ethereum.Value.fromString(metadataURI)
    )
  )
  verifiedPoCEvent.parameters.push(
    new ethereum.EventParam("severity", ethereum.Value.fromString(severity))
  )
  verifiedPoCEvent.parameters.push(
    new ethereum.EventParam("summary", ethereum.Value.fromString(summary))
  )

  return verifiedPoCEvent
}
