use substreams::errors::Error;
use substreams_ethereum::pb::eth::v2 as eth;
use hex;

mod pb;

use pb::pulseproof::{CandidateEvent, CandidateEvents};

// ERC20 canonical topics (paste exact hex strings)
const TRANSFER_TOPIC: &str =
    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef";
const APPROVAL_TOPIC: &str =
    "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925";
const SWAP_TOPIC: &str = "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1";
const PERMIT_TOPIC: &str = "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925";
const FLASHLOAN_TOPIC: &str = "0x8a8c523c5f1c4d3f7f";


#[substreams::handlers::map]
fn map_candidate_events(blk: eth::Block) -> Result<CandidateEvents, Error> {
    let mut events_vec: Vec<CandidateEvent> = Vec::new();
    
    for tx in blk.transaction_traces.iter() {
        let tx_hash = format!("0x{}", hex::encode(&tx.hash));

        if let Some(receipt) = &tx.receipt {
            for log in receipt.logs.iter() {
                let topic0 = log.topics.get(0).map(|t| format!("0x{}", hex::encode(t))).unwrap_or_default();
                let topics_vec: Vec<String> = log
                    .topics
                    .iter()
                    .map(|t| format!("0x{}", hex::encode(t)))
                    .collect();
                let data_hex = format!("0x{}", hex::encode(&log.data));

                let block_number = blk.number;
                let log_index = log.index as u64;
                let contract_addr = format!("0x{}", hex::encode(&log.address));

                if topic0 == TRANSFER_TOPIC {
                    events_vec.push(CandidateEvent {
                        transaction_hash: tx_hash.clone(),
                        block_number,
                        log_index,
                        contract_address: contract_addr.clone(),
                        event_signature: TRANSFER_TOPIC.to_string(),
                        event_type: "Transfer".to_string(),
                        metadata: format!("{{\"topics\":{:?},\"data\":\"{}\"}}",topics_vec, data_hex),
                    });
                } else if topic0 == APPROVAL_TOPIC {
                    events_vec.push(CandidateEvent {
                        transaction_hash: tx_hash.clone(),
                        block_number,
                        log_index,
                        contract_address: contract_addr.clone(),
                        event_signature: APPROVAL_TOPIC.to_string(),
                        event_type: "Approval".to_string(),
                        metadata: format!(
                            "{{\"topics\":{:?},\"data\":\"{}\"}}",
                            topics_vec, data_hex
                        ),
                    });
                } else if topic0 == SWAP_TOPIC {
                    events_vec.push(CandidateEvent {
                        transaction_hash: tx_hash.clone(),
                        block_number,
                        log_index,
                        contract_address: contract_addr.clone(),
                        event_signature: SWAP_TOPIC.to_string(),
                        event_type: "Swap".to_string(),
                        metadata: format!(
                            "{{\"topics\":{:?},\"data\":\"{}\"}}",
                            topics_vec, data_hex
                        ),
                    });
                } else if topic0 == PERMIT_TOPIC {
                    events_vec.push(CandidateEvent {
                        transaction_hash: tx_hash.clone(),
                        block_number,
                        log_index,
                        contract_address: contract_addr.clone(),
                        event_signature: PERMIT_TOPIC.to_string(),
                        event_type: "Permit".to_string(),
                        metadata: format!(
                            "{{\"topics\":{:?},\"data\":\"{}\"}}",
                            topics_vec, data_hex
                        ),
                    });

                
                } else if topic0 == FLASHLOAN_TOPIC {
                    events_vec.push(CandidateEvent {
                        transaction_hash: tx_hash.clone(),
                        block_number,
                        log_index,
                        contract_address: contract_addr.clone(),
                        event_signature: FLASHLOAN_TOPIC.to_string(),
                        event_type: "FlashLoan".to_string(),
                        metadata: format!(
                            "{{\"topics\":{:?},\"data\":\"{}\"}}",
                            topics_vec, data_hex
                        ),
                    });

                }
            }
    }
}
    
    Ok(CandidateEvents { events: events_vec })
}
