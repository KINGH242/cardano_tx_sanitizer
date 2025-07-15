"""
Cardano Transaction Parser & Exporter GUI
"""

from pathlib import Path

from pycardano import TransactionWitnessSet
from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont, QPalette
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from cardano_tx_sanitizer.transaction_parser import (
    CollectionType,
    Era,
    TransactionParser,
)
from cardano_tx_sanitizer.utils import dump_json_file


class MainWindow(QMainWindow):
    """
    Main application window for the Cardano Transaction Parser & Exporter.
    """

    def __init__(self):
        super(MainWindow, self).__init__()

        self.parser = TransactionParser()
        self.transaction_data = None

        self.setWindowTitle("Cardano Transaction Parser & Exporter")
        self.setGeometry(100, 100, 1000, 700)

        # Create main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create splitter for left and right panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(splitter)

        # Left panel - Controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel - Transaction view
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        # Set initial splitter sizes
        splitter.setSizes([300, 700])

    def create_left_panel(self):
        """Create the left control panel"""
        left_widget = QWidget()
        layout = QVBoxLayout(left_widget)

        # File selection group
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)

        # Drag and drop area
        drag_drop_frame = QFrame()
        drag_drop_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        drag_drop_frame.setAcceptDrops(True)

        # Create and set palette for drag and drop area
        palette = QPalette()
        palette.setColor(QPalette.Window, Qt.lightGray)
        drag_drop_frame.setPalette(palette)
        drag_drop_frame.setAutoFillBackground(True)
        drag_drop_frame.setFixedHeight(80)
        file_layout.addWidget(drag_drop_frame)

        font = QFont()
        font.setPointSize(10)
        font.setBold(True)

        self.drag_drop_label = QLabel("Drag and drop a JSON file here")
        self.drag_drop_label.setAlignment(Qt.AlignCenter)
        self.drag_drop_label.setFont(font)
        drag_drop_layout = QVBoxLayout()
        drag_drop_layout.addWidget(self.drag_drop_label)
        drag_drop_frame.setLayout(drag_drop_layout)

        self.file_label = QLabel("No file selected")
        self.file_label.setWordWrap(True)
        file_layout.addWidget(self.file_label)

        self.file_button = QPushButton("Open JSON File")
        self.file_button.clicked.connect(self.open_file_dialog)
        file_layout.addWidget(self.file_button)

        layout.addWidget(file_group)

        # Connect drag and drop events
        drag_drop_frame.dragEnterEvent = self.drag_enter_event
        drag_drop_frame.dropEvent = self.drop_event

        # Export options group
        export_group = QGroupBox("Export Options")
        export_layout = QVBoxLayout(export_group)

        export_layout.addWidget(QLabel("Era Format:"))
        self.era_combo = QComboBox()
        self.era_combo.addItems(["Babbage Era", "Conway Era"])
        export_layout.addWidget(self.era_combo)

        export_layout.addWidget(QLabel("Collection Type:"))
        self.collection_combo = QComboBox()
        self.collection_combo.addItems(
            [
                CollectionType.DEFAULT.value,
                CollectionType.LIST.value,
                CollectionType.SET.value,
            ]
        )
        export_layout.addWidget(self.collection_combo)

        export_layout.addWidget(QLabel("Output Format:"))
        self.output_format_combo = QComboBox()
        self.output_format_combo.addItems(["JSON", "CBOR Hex"])
        export_layout.addWidget(self.output_format_combo)

        layout.addWidget(export_group)

        # Action buttons
        self.view_button = QPushButton("View Parsed Transaction")
        self.view_button.clicked.connect(self.view_transaction)
        self.view_button.setEnabled(False)
        layout.addWidget(self.view_button)

        self.export_button = QPushButton("Export Transaction")
        self.export_button.clicked.connect(self.export_transaction)
        self.export_button.setEnabled(False)
        layout.addWidget(self.export_button)

        self.save_button = QPushButton("Save Export to File")
        self.save_button.clicked.connect(self.save_export_to_file)
        self.save_button.setEnabled(False)
        layout.addWidget(self.save_button)

        # Add stretch to push everything to top
        layout.addStretch()

        return left_widget

    def create_right_panel(self):
        """Create the right transaction view panel"""
        right_widget = QWidget()
        layout = QVBoxLayout(right_widget)

        # Transaction view
        layout.addWidget(QLabel("Transaction View:"))

        self.transaction_view = QTextEdit()
        self.transaction_view.setReadOnly(True)
        self.transaction_view.setPlainText(
            "Load a JSON file to view the parsed transaction..."
        )
        layout.addWidget(self.transaction_view)

        # Export output
        layout.addWidget(QLabel("Export Output:"))

        self.export_view = QTextEdit()
        self.export_view.setReadOnly(True)
        self.export_view.setPlainText("Export a transaction to see the output...")
        layout.addWidget(self.export_view)

        return right_widget

    def open_file_dialog(self):
        """Open file dialog to select JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open JSON File",
            "",
            "TX Files (*.tx);;JSON Files (*.json);;All Files (*)",
        )

        if file_path:
            self.parse_json_file(file_path)

    def parse_json_file(self, file_path):
        """Parse the selected JSON file"""
        try:
            self.transaction_data = self.parser.parse_from_json(file_path)

            # Update UI
            self.file_label.setText(f"File: {file_path}")
            self.view_button.setEnabled(True)
            self.export_button.setEnabled(True)

            # Show success message
            QMessageBox.information(self, "Success", "Transaction parsed successfully!")

            # Automatically view the transaction
            self.view_transaction()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to parse JSON file: {e}")
            self.file_label.setText("No file selected")
            self.view_button.setEnabled(False)
            self.export_button.setEnabled(False)
            self.save_button.setEnabled(False)

    def drag_enter_event(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def drop_event(self, event: QDropEvent):
        """Handle drop events"""
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.parse_json_file(file_path)

    def view_transaction(self):
        """Display the parsed transaction in the view"""
        if not self.transaction_data:
            return

        try:
            self.transaction_view.setPlainText(str(self.transaction_data.transaction))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display transaction: {e}")

    def export_transaction(self):
        """Export the transaction with selected options"""
        if not self.transaction_data:
            QMessageBox.warning(self, "Warning", "No transaction data to export!")
            return

        try:
            # Get selected options
            era_text = self.era_combo.currentText()
            era = Era.BABBAGE if era_text == "Babbage Era" else Era.CONWAY

            collection_text = self.collection_combo.currentText()
            collection_type = CollectionType[collection_text.upper()]

            output_format = self.output_format_combo.currentText().lower()

            # Export transaction
            if output_format == "json":
                exported_data = self.parser.export_transaction(
                    era, collection_type, "json"
                )
            else:  # CBOR Hex
                exported_data = self.parser.export_transaction(
                    era, collection_type, "hex"
                )

            # Display exported data
            self.export_view.setPlainText(str(exported_data))
            self.save_button.setEnabled(True)

            QMessageBox.information(
                self,
                "Success",
                f"Transaction exported as {era_text} with {collection_text} collections!",
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export transaction: {e}")

    def save_export_to_file(self):
        """Save the exported transaction to a file"""
        if not self.export_view.toPlainText():
            QMessageBox.warning(self, "Warning", "No export data to save!")
            return

        # Determine file extension based on output format
        output_format = self.output_format_combo.currentText().lower()
        extension = "json" if output_format == "json" else "txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Export",
            f"exported_transaction.{extension}",
            f"{extension.upper()} Files (*.{extension});;All Files (*)",
        )

        if file_path:
            try:
                transaction = self.transaction_data.transaction

                era_text = self.era_combo.currentText()
                era = Era.BABBAGE if era_text == "Babbage Era" else Era.CONWAY

                def is_empty(witness_set: TransactionWitnessSet) -> bool:
                    """Check if the witness set is empty."""
                    return (
                        not witness_set.vkey_witnesses
                        and not witness_set.native_scripts
                        and not witness_set.bootstrap_witness
                        and not witness_set.plutus_v1_script
                        and not witness_set.plutus_data
                        and not witness_set.redeemer
                        and not witness_set.plutus_v2_script
                        and not witness_set.plutus_v3_script
                    )

                tx_status = (
                    "Unwitnessed"
                    if is_empty(transaction.transaction_witness_set)
                    else "Signed"
                )

                tx_json = {
                    "type": f"{tx_status} Tx {era.name.capitalize()}Era",
                    "description": "Generated by Cardano Transaction Sanitizer",
                    "cborHex": self.transaction_data.transaction.to_cbor_hex(),
                }

                dump_json_file(Path(file_path), tx_json)

                # with open(file_path, 'w') as file:
                #     file.write(self.export_view.toPlainText())

                QMessageBox.information(self, "Success", f"Export saved to {file_path}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save export: {e}")
