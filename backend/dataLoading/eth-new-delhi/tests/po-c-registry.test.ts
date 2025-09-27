import {
  assert,
  describe,
  test,
  clearStore,
  beforeAll,
  afterAll
} from "matchstick-as/assembly/index"
import { Bytes, Address, BigInt } from "@graphprotocol/graph-ts"
import { VerifiedPoC } from "../generated/schema"
import { VerifiedPoC as VerifiedPoCEvent } from "../generated/PoCRegistry/PoCRegistry"
import { handleVerifiedPoC } from "../src/po-c-registry"
import { createVerifiedPoCEvent } from "./po-c-registry-utils"

// Tests structure (matchstick-as >=0.5.0)
// https://thegraph.com/docs/en/subgraphs/developing/creating/unit-testing-framework/#tests-structure

describe("Describe entity assertions", () => {
  beforeAll(() => {
    let pocHash = Bytes.fromI32(1234567890)
    let target = Address.fromString(
      "0x0000000000000000000000000000000000000001"
    )
    let attackedVictimBlockNumber = BigInt.fromI32(234)
    let pocType = "Example string value"
    let metadataURI = "Example string value"
    let severity = "Example string value"
    let summary = "Example string value"
    let newVerifiedPoCEvent = createVerifiedPoCEvent(
      pocHash,
      target,
      attackedVictimBlockNumber,
      pocType,
      metadataURI,
      severity,
      summary
    )
    handleVerifiedPoC(newVerifiedPoCEvent)
  })

  afterAll(() => {
    clearStore()
  })

  // For more test scenarios, see:
  // https://thegraph.com/docs/en/subgraphs/developing/creating/unit-testing-framework/#write-a-unit-test

  test("VerifiedPoC created and stored", () => {
    assert.entityCount("VerifiedPoC", 1)

    // 0xa16081f360e3847006db660bae1c6d1b2e17ec2a is the default address used in newMockEvent() function
    assert.fieldEquals(
      "VerifiedPoC",
      "0xa16081f360e3847006db660bae1c6d1b2e17ec2a-1",
      "pocHash",
      "1234567890"
    )
    assert.fieldEquals(
      "VerifiedPoC",
      "0xa16081f360e3847006db660bae1c6d1b2e17ec2a-1",
      "target",
      "0x0000000000000000000000000000000000000001"
    )
    assert.fieldEquals(
      "VerifiedPoC",
      "0xa16081f360e3847006db660bae1c6d1b2e17ec2a-1",
      "attackedVictimBlockNumber",
      "234"
    )
    assert.fieldEquals(
      "VerifiedPoC",
      "0xa16081f360e3847006db660bae1c6d1b2e17ec2a-1",
      "pocType",
      "Example string value"
    )
    assert.fieldEquals(
      "VerifiedPoC",
      "0xa16081f360e3847006db660bae1c6d1b2e17ec2a-1",
      "metadataURI",
      "Example string value"
    )
    assert.fieldEquals(
      "VerifiedPoC",
      "0xa16081f360e3847006db660bae1c6d1b2e17ec2a-1",
      "severity",
      "Example string value"
    )
    assert.fieldEquals(
      "VerifiedPoC",
      "0xa16081f360e3847006db660bae1c6d1b2e17ec2a-1",
      "summary",
      "Example string value"
    )

    // More assert options:
    // https://thegraph.com/docs/en/subgraphs/developing/creating/unit-testing-framework/#asserts
  })
})
