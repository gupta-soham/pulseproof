import { newMockEvent } from "matchstick-as"
import { ethereum, Bytes, Address } from "@graphprotocol/graph-ts"
import { VerifiedPoC } from "../generated/PoCRegistry/PoCRegistry"

export function createVerifiedPoCEvent(
  pocHash: Bytes,
  pocType: string,
  target: Address,
  metadataURI: string,
  hederaTx: string
): VerifiedPoC {
  let verifiedPoCEvent = changetype<VerifiedPoC>(newMockEvent())

  verifiedPoCEvent.parameters = new Array()

  verifiedPoCEvent.parameters.push(
    new ethereum.EventParam("pocHash", ethereum.Value.fromFixedBytes(pocHash))
  )
  verifiedPoCEvent.parameters.push(
    new ethereum.EventParam("pocType", ethereum.Value.fromString(pocType))
  )
  verifiedPoCEvent.parameters.push(
    new ethereum.EventParam("target", ethereum.Value.fromAddress(target))
  )
  verifiedPoCEvent.parameters.push(
    new ethereum.EventParam(
      "metadataURI",
      ethereum.Value.fromString(metadataURI)
    )
  )
  verifiedPoCEvent.parameters.push(
    new ethereum.EventParam("hederaTx", ethereum.Value.fromString(hederaTx))
  )

  return verifiedPoCEvent
}
