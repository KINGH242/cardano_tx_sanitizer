"""
Transaction Parser and Exporter for Cardano Transactions
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Union

# PyCardano imports
from pycardano import (
    Certificate,
    NonEmptyOrderedSet,
    OrderedSet,
    PoolParams,
    PoolRegistration,
    Transaction,
    TransactionBody,
    TransactionWitnessSet,
)

from cardano_tx_sanitizer.utils import load_json_file


class Era(Enum):
    BABBAGE = "babbage"
    CONWAY = "conway"


class CollectionType(Enum):
    DEFAULT = "Default"
    LIST = "List"
    SET = "Set"


@dataclass
class TransactionData:
    """Represents parsed transaction data from CBOR hex using PyCardano"""

    cbor_hex: str
    transaction: Transaction

    def __init__(self, cbor_hex: str):
        self.cbor_hex = cbor_hex
        self.transaction = self._parse_transaction(cbor_hex)

    def _parse_transaction(self, cbor_hex: str) -> Transaction:
        """Parse CBOR hex string to PyCardano Transaction object"""
        try:
            cbor_bytes = bytes.fromhex(cbor_hex)
            return Transaction.from_cbor(cbor_bytes)
        except Exception as e:
            raise ValueError(f"Invalid CBOR hex or transaction format: {e}")


class TransactionExporter:
    """Handles exporting transaction data to different era formats"""

    def __init__(self, transaction: Transaction):
        self.transaction = transaction

    def export_to_era(self, era: Era, collection_type: CollectionType) -> Transaction:
        """Export transaction data to specified era format"""
        if era == Era.BABBAGE:
            return self._export_babbage(collection_type)
        elif era == Era.CONWAY:
            return self._export_conway(collection_type)
        else:
            raise ValueError(f"Unsupported era: {era}")

    def _build_babbage_transaction_body(self, tx_body, collection_type: CollectionType):
        """Build transaction body according to Babbage CDDL specification"""
        # Babbage CDDL field types:
        # 0: set<transaction_input> (inputs)
        # 1: [* transaction_output] (outputs - always list)
        # 4: [* certificate] (certificates)
        # 13: set<transaction_input> (collateral)
        # 14: set<addr_keyhash> (required_signers)
        # 18: set<transaction_input> (reference_inputs)

        # Handle DEFAULT collection type for Babbage era
        if (
            collection_type == CollectionType.DEFAULT
            or collection_type == CollectionType.SET
        ):
            # Use CDDL-specified types
            inputs = OrderedSet(tx_body.inputs) if tx_body.inputs else None
            collateral = (
                NonEmptyOrderedSet(tx_body.collateral) if tx_body.collateral else None
            )
            required_signers = (
                NonEmptyOrderedSet(tx_body.required_signers)
                if tx_body.required_signers
                else None
            )
            reference_inputs = (
                NonEmptyOrderedSet(tx_body.reference_inputs)
                if tx_body.reference_inputs
                else None
            )
        else:
            inputs = list(tx_body.inputs) if tx_body.inputs else None
            collateral = list(tx_body.collateral) if tx_body.collateral else None
            required_signers = (
                list(tx_body.required_signers) if tx_body.required_signers else None
            )
            reference_inputs = (
                list(tx_body.reference_inputs) if tx_body.reference_inputs else None
            )

        # Process certificates to handle stake pool registration
        if tx_body.certificates:
            certificates = self.process_certificates(
                tx_body.certificates, Era.BABBAGE, collection_type
            )
            # Convert back to appropriate collection type if needed
            if (
                collection_type == CollectionType.DEFAULT
                or collection_type == CollectionType.LIST
            ):
                certificates = list(certificates)
            else:  # SET
                certificates = NonEmptyOrderedSet(certificates)
        else:
            certificates = None

        return TransactionBody(
            inputs=inputs,
            outputs=tx_body.outputs,
            fee=tx_body.fee,
            ttl=tx_body.ttl,
            certificates=certificates,
            withdraws=tx_body.withdraws,
            update=tx_body.update,
            auxiliary_data_hash=tx_body.auxiliary_data_hash,
            validity_start=tx_body.validity_start,
            mint=tx_body.mint,
            script_data_hash=tx_body.script_data_hash,
            collateral=collateral,
            required_signers=required_signers,
            network_id=tx_body.network_id,
            collateral_return=tx_body.collateral_return,
            total_collateral=tx_body.total_collateral,
            reference_inputs=reference_inputs,
        )

    def _build_babbage_witness_set(
        self, witness_set: TransactionWitnessSet, collection_type: CollectionType
    ):
        """Build witness set according to Babbage CDDL specification"""

        if (
            collection_type == CollectionType.DEFAULT
            or collection_type == CollectionType.LIST
        ):
            # Use CDDL-specified types
            vkey_witnesses = (
                list(witness_set.vkey_witnesses) if witness_set.vkey_witnesses else None
            )
            native_scripts = (
                list(witness_set.native_scripts) if witness_set.native_scripts else None
            )
            bootstrap_witness = (
                list(witness_set.bootstrap_witness)
                if witness_set.bootstrap_witness
                else None
            )
            plutus_v1_script = (
                list(witness_set.plutus_v1_script)
                if witness_set.plutus_v1_script
                else None
            )
            plutus_v2_script = (
                list(witness_set.plutus_v2_script)
                if witness_set.plutus_v2_script
                else None
            )
            plutus_v3_script = (
                list(witness_set.plutus_v3_script)
                if witness_set.plutus_v3_script
                else None
            )
            plutus_data = (
                list(witness_set.plutus_data) if witness_set.plutus_data else None
            )
            redeemer = list(witness_set.redeemer) if witness_set.redeemer else None
        else:
            vkey_witnesses = (
                NonEmptyOrderedSet(witness_set.vkey_witnesses)
                if witness_set.vkey_witnesses
                else None
            )
            native_scripts = (
                NonEmptyOrderedSet(witness_set.native_scripts)
                if witness_set.native_scripts
                else None
            )
            bootstrap_witness = (
                NonEmptyOrderedSet(witness_set.bootstrap_witness)
                if witness_set.bootstrap_witness
                else None
            )
            plutus_v1_script = (
                NonEmptyOrderedSet(witness_set.plutus_v1_script)
                if witness_set.plutus_v1_script
                else None
            )
            plutus_v2_script = (
                NonEmptyOrderedSet(witness_set.plutus_v2_script)
                if witness_set.plutus_v2_script
                else None
            )
            plutus_v3_script = (
                NonEmptyOrderedSet(witness_set.plutus_v3_script)
                if witness_set.plutus_v3_script
                else None
            )
            plutus_data = (
                NonEmptyOrderedSet(witness_set.plutus_data)
                if witness_set.plutus_data
                else None
            )
            redeemer = (
                NonEmptyOrderedSet(witness_set.redeemer)
                if witness_set.redeemer
                else None
            )

        return TransactionWitnessSet(
            vkey_witnesses=vkey_witnesses,
            native_scripts=native_scripts,
            bootstrap_witness=bootstrap_witness,
            plutus_v1_script=plutus_v1_script,
            plutus_v2_script=plutus_v2_script,
            plutus_v3_script=plutus_v3_script,
            plutus_data=plutus_data,
            redeemer=redeemer,
        )

    def _export_babbage(self, collection_type: CollectionType) -> Transaction:
        """Export to Babbage era Transaction object"""
        body = self._build_babbage_transaction_body(
            self.transaction.transaction_body, collection_type
        )
        witness_set = self._build_babbage_witness_set(
            self.transaction.transaction_witness_set, collection_type
        )

        return Transaction(
            transaction_body=body,
            transaction_witness_set=witness_set,
            auxiliary_data=self.transaction.auxiliary_data,
            valid=self.transaction.valid,
        )

    def _build_conway_transaction_body(self, tx_body, collection_type: CollectionType):
        """Build transaction body according to Conway CDDL specification"""
        # Conway CDDL field types:
        # 0: set<transaction_input> (inputs)
        # 1: [* transaction_output] (outputs - always list)
        # 4: nonempty_set<certificate> (certificates)
        # 13: set<transaction_input> (collateral)
        # 14: set<addr_keyhash> (required_signers)
        # 18: set<transaction_input> (reference_inputs)

        # Handle DEFAULT collection type for Conway era
        if (
            collection_type == CollectionType.DEFAULT
            or collection_type == CollectionType.SET
        ):
            # Use CDDL-specified types
            inputs = OrderedSet(tx_body.inputs) if tx_body.inputs else set()
            collateral = (
                NonEmptyOrderedSet(tx_body.collateral) if tx_body.collateral else None
            )
            required_signers = (
                NonEmptyOrderedSet(tx_body.required_signers)
                if tx_body.required_signers
                else None
            )
            reference_inputs = (
                NonEmptyOrderedSet(tx_body.reference_inputs)
                if tx_body.reference_inputs
                else None
            )
        else:
            inputs = list(tx_body.inputs) if tx_body.inputs else []
            collateral = list(tx_body.collateral) if tx_body.collateral else None
            required_signers = (
                list(tx_body.required_signers) if tx_body.required_signers else None
            )
            reference_inputs = (
                list(tx_body.reference_inputs) if tx_body.reference_inputs else None
            )

        # Process certificates to handle stake pool registration
        if tx_body.certificates:
            certificates = self.process_certificates(
                tx_body.certificates, Era.CONWAY, collection_type
            )
            # Convert back to appropriate collection type if needed
            if (
                collection_type == CollectionType.DEFAULT
                or collection_type == CollectionType.SET
            ):
                certificates = NonEmptyOrderedSet(certificates)
            elif collection_type == CollectionType.LIST:
                certificates = list(certificates)
        else:
            certificates = None

        return TransactionBody(
            inputs=inputs,
            outputs=tx_body.outputs,
            fee=tx_body.fee,
            ttl=tx_body.ttl,
            certificates=certificates,
            withdraws=tx_body.withdraws,
            update=tx_body.update,
            auxiliary_data_hash=tx_body.auxiliary_data_hash,
            validity_start=tx_body.validity_start,
            mint=tx_body.mint,
            script_data_hash=tx_body.script_data_hash,
            collateral=collateral,
            required_signers=required_signers,
            network_id=tx_body.network_id,
            collateral_return=tx_body.collateral_return,
            total_collateral=tx_body.total_collateral,
            reference_inputs=reference_inputs,
        )

    def _build_conway_witness_set(
        self, witness_set: TransactionWitnessSet, collection_type: CollectionType
    ):
        """Build witness set according to Babbage CDDL specification"""

        if (
            collection_type == CollectionType.DEFAULT
            or collection_type == CollectionType.SET
        ):
            # Use CDDL-specified types
            vkey_witnesses = (
                NonEmptyOrderedSet(witness_set.vkey_witnesses)
                if witness_set.vkey_witnesses
                else None
            )
            native_scripts = (
                NonEmptyOrderedSet(witness_set.native_scripts)
                if witness_set.native_scripts
                else None
            )
            bootstrap_witness = (
                NonEmptyOrderedSet(witness_set.bootstrap_witness)
                if witness_set.bootstrap_witness
                else None
            )
            plutus_v1_script = (
                NonEmptyOrderedSet(witness_set.plutus_v1_script)
                if witness_set.plutus_v1_script
                else None
            )
            plutus_v2_script = (
                NonEmptyOrderedSet(witness_set.plutus_v2_script)
                if witness_set.plutus_v2_script
                else None
            )
            plutus_v3_script = (
                NonEmptyOrderedSet(witness_set.plutus_v3_script)
                if witness_set.plutus_v3_script
                else None
            )
            plutus_data = (
                NonEmptyOrderedSet(witness_set.plutus_data)
                if witness_set.plutus_data
                else None
            )
            redeemer = (
                NonEmptyOrderedSet(witness_set.redeemer)
                if witness_set.redeemer
                else None
            )
        else:
            vkey_witnesses = (
                list(witness_set.vkey_witnesses) if witness_set.vkey_witnesses else None
            )
            native_scripts = (
                list(witness_set.native_scripts) if witness_set.native_scripts else None
            )
            bootstrap_witness = (
                list(witness_set.bootstrap_witness)
                if witness_set.bootstrap_witness
                else None
            )
            plutus_v1_script = (
                list(witness_set.plutus_v1_script)
                if witness_set.plutus_v1_script
                else None
            )
            plutus_v2_script = (
                list(witness_set.plutus_v2_script)
                if witness_set.plutus_v2_script
                else None
            )
            plutus_v3_script = (
                list(witness_set.plutus_v3_script)
                if witness_set.plutus_v3_script
                else None
            )
            plutus_data = (
                list(witness_set.plutus_data) if witness_set.plutus_data else None
            )
            redeemer = list(witness_set.redeemer) if witness_set.redeemer else None

        return TransactionWitnessSet(
            vkey_witnesses=vkey_witnesses,
            native_scripts=native_scripts,
            bootstrap_witness=bootstrap_witness,
            plutus_v1_script=plutus_v1_script,
            plutus_v2_script=plutus_v2_script,
            plutus_v3_script=plutus_v3_script,
            plutus_data=plutus_data,
            redeemer=redeemer,
        )

    def _export_conway(self, collection_type: CollectionType) -> Transaction:
        """Export to Conway era Transaction object"""
        # Using the transaction as-is with proper CDDL builder logic if available
        body = self._build_conway_transaction_body(
            self.transaction.transaction_body, collection_type
        )
        witness_set = self._build_conway_witness_set(
            self.transaction.transaction_witness_set, collection_type
        )

        return Transaction(
            transaction_body=body,
            transaction_witness_set=witness_set,
            auxiliary_data=self.transaction.auxiliary_data,
            valid=self.transaction.valid,
        )

    def process_certificates(
        self, certificates: List[Certificate], era: Era, collection_type: CollectionType
    ) -> List[Certificate]:
        """Process certificates and handle stake pool registration certificates according to era CDDL"""
        if not certificates:
            return certificates

        processed_certificates = []

        for cert in certificates:
            if isinstance(cert, PoolRegistration):
                # Process stake pool registration certificate
                processed_cert = self._process_pool_registration_cert(
                    cert, collection_type
                )
                processed_certificates.append(processed_cert)
            else:
                # Keep other certificates as-is
                processed_certificates.append(cert)

        return processed_certificates

    def _process_pool_registration_cert(
        self, cert: PoolRegistration, collection_type: CollectionType
    ) -> PoolRegistration:
        """Process stake pool registration certificate according to era CDDL specification"""
        if not cert.pool_params:
            return cert

        # Get the pool_owners field from pool_params
        pool_owners = cert.pool_params.pool_owners

        if not pool_owners:
            return cert

        if (
            collection_type == CollectionType.DEFAULT
            or collection_type == CollectionType.SET
        ):
            processed_pool_owners = OrderedSet(pool_owners)
        else:
            processed_pool_owners = list(pool_owners)

        # Create new PoolParams with processed pool_owners
        new_pool_params = PoolParams(
            operator=cert.pool_params.operator,
            vrf_keyhash=cert.pool_params.vrf_keyhash,
            pledge=cert.pool_params.pledge,
            cost=cert.pool_params.cost,
            margin=cert.pool_params.margin,
            reward_account=cert.pool_params.reward_account,
            pool_owners=processed_pool_owners,
            relays=cert.pool_params.relays,
            pool_metadata=cert.pool_params.pool_metadata,
        )

        # Create new PoolRegistration with processed pool_params
        return PoolRegistration(
            pool_params=new_pool_params,
        )

    def export_to_json(
        self, era: Era, collection_type: CollectionType, indent: int = 2
    ) -> str:
        """Export to JSON string using PyCardano's Transaction serialization"""
        transaction = self.export_to_era(era, collection_type)

        return str(transaction)

    def export_to_cbor(self, era: Era, collection_type: CollectionType) -> bytes:
        """Export to CBOR bytes using PyCardano's Transaction serialization"""
        transaction = self.export_to_era(era, collection_type)
        return transaction.to_cbor()

    def export_to_hex(self, era: Era, collection_type: CollectionType) -> str:
        """Export to hex string using PyCardano's Transaction serialization"""
        cbor_bytes = self.export_to_cbor(era, collection_type)
        return cbor_bytes.hex()


class TransactionParser:
    """Main class for parsing and exporting Cardano transactions"""

    def __init__(self):
        self.transaction_data = None

    def parse_from_json(self, json_file_path: str) -> TransactionData:
        """Parse transaction from JSON file containing cborHex"""
        try:
            data = load_json_file(Path(json_file_path))

            if "cborHex" not in data:
                raise ValueError("JSON file must contain 'cborHex' field")

            cbor_hex = data["cborHex"]
            self.transaction_data = TransactionData(cbor_hex)
            return self.transaction_data

        except Exception as e:
            raise ValueError(f"Failed to parse JSON file: {e}")

    def parse_from_cbor_hex(self, cbor_hex: str) -> TransactionData:
        """Parse transaction from CBOR hex string"""
        self.transaction_data = TransactionData(cbor_hex)
        return self.transaction_data

    def get_exporter(self) -> TransactionExporter:
        """Get exporter for current transaction data"""
        if self.transaction_data is None:
            raise ValueError(
                "No transaction data to export. Parse a transaction first."
            )
        return TransactionExporter(self.transaction_data.transaction)

    def export_transaction(
        self, era: Era, collection_type: CollectionType, output_format: str = "json"
    ) -> Union[str, bytes]:
        """Export transaction to specified format"""
        exporter = self.get_exporter()

        if output_format.lower() == "json":
            return exporter.export_to_json(era, collection_type)
        elif output_format.lower() == "cbor":
            return exporter.export_to_cbor(era, collection_type)
        elif output_format.lower() == "hex":
            return exporter.export_to_hex(era, collection_type)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
