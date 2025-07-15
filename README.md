# Cardano Transaction Sanitizer

Cardano Transaction Sanitizer is a Python application for parsing and exporting Cardano transactions, designed to handle both Babbage and Conway eras.

## Features

- **Drag and Drop:** Easily drag and drop JSON transaction files into the application.
- **File Selection:** Use the file dialog to choose your transaction files for parsing.
- **Era and Collection Type Options:** Customize transaction export for Babbage or Conway era with selectable collection types (Default, List, Set).
- **Export Formats:** Export transactions in JSON or CBOR Hex format.
- **View Parsed Transactions:** Inspect the structure of parsed transactions directly within the app.
- **Save Exports to File:** Save your exports as JSON or text files.

## Usage

1. **Open the Application:**
   - Run the application using `uv run cardano-tx-sanitizer`.

2. **Load a Transaction:**
   - Use the "Open JSON File" button or drag and drop a JSON file containing your transaction.

3. **Select Export Options:**
   - Choose the desired Era and Collection Type.
   - Select your preferred output format (JSON or CBOR Hex).

4. **View and Export:**
   - Click "View Parsed Transaction" to see the transaction details.
   - Click "Export Transaction" to process the export.
   - Use "Save Export to File" to save your outputs.

## Development

### Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/KINGH242/cardano_tx_sanitizer.git
   ```

2. **Navigate to the project directory:**

   ```bash
   cd cardano_tx_sanitizer
   ```

3. **Install dependencies:**

   - Ensure you have Python 3.13+ installed.
   - Install uv if you haven't already:

   ```bash
   pip install uv
   ```

   - Then, install required packages:

   ```bash
   uv sync
   ```

### Running Tests

- Run all tests: `make test`
- Static Analysis: `make qa`
- Code Formatting: `make format`

### Building and Distribution

- To build and create app using pyinstaller: `make create-app`
- To create a disk image on macOS: `make create-disk-image`

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for review.

## License

This project is licensed under the MIT License.
