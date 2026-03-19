let pyodide;
let formatNc;
let makeOutputFilename;
let outputText = "";
let outputFilename = "formatted.tap";

const fileInput = document.getElementById("fileInput");
const runButton = document.getElementById("runButton");
const downloadButton = document.getElementById("downloadButton");
const statusEl = document.getElementById("status");
const preview = document.getElementById("preview");

function setStatus(message) {
  statusEl.textContent = message;
}

function hasFileSelected() {
  return fileInput.files && fileInput.files.length > 0;
}

function updateRunButton() {
  runButton.disabled = !(pyodide && formatNc && hasFileSelected());
}

async function initializePython() {
  try {
    pyodide = await loadPyodide();

    const response = await fetch("formatter_core.py", { cache: "no-store" });
    if (!response.ok) {
      throw new Error("Could not load formatter_core.py");
    }

    const pythonSource = await response.text();
    await pyodide.runPythonAsync(pythonSource);

    formatNc = pyodide.globals.get("format_nc");
    makeOutputFilename = pyodide.globals.get("make_output_filename");

    setStatus("Python runtime ready. Select a file and click Run Formatter.");
    runButton.textContent = "Run Formatter";
    updateRunButton();
  } catch (error) {
    setStatus(`Initialization failed: ${error.message}`);
    runButton.textContent = "Python failed to load";
    runButton.disabled = true;
  }
}

async function runFormatter() {
  if (!hasFileSelected() || !formatNc || !makeOutputFilename) {
    return;
  }

  const selectedFile = fileInput.files[0];

  try {
    setStatus(`Processing ${selectedFile.name}...`);

    const sourceText = await selectedFile.text();
    outputText = formatNc(sourceText).toString();
    outputFilename = makeOutputFilename(selectedFile.name).toString();

    preview.value = outputText;
    downloadButton.disabled = false;
    setStatus(`Done. Output file is ${outputFilename}`);
  } catch (error) {
    outputText = "";
    downloadButton.disabled = true;
    setStatus(`Formatting failed: ${error.message}`);
  }
}

function downloadOutput() {
  if (!outputText) {
    return;
  }

  const blob = new Blob([outputText], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = outputFilename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

fileInput.addEventListener("change", () => {
  downloadButton.disabled = true;
  outputText = "";
  preview.value = "";
  updateRunButton();

  if (hasFileSelected()) {
    setStatus(`Selected: ${fileInput.files[0].name}`);
  }
});

runButton.addEventListener("click", runFormatter);
downloadButton.addEventListener("click", downloadOutput);

initializePython();
