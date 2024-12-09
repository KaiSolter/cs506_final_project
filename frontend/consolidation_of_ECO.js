const fs = require("fs");
const path = require("path");

// Directories
const inputDir = "./frontend/eco.json-master/json_files"; // Folder where JSON files are stored
const outputFile = "ecoMapping.json"; // Output file path

// Initialize an empty mapping object
const ecoMapping = {};

// Function to process a single file
function processFile(filePath) {
  const data = JSON.parse(fs.readFileSync(filePath, "utf8"));
  
  // Iterate through each entry in the JSON file
  for (const key in data) {
    const entry = data[key];
    
    // Check if both "eco" and "name" exist in the current entry
    if (entry.eco && entry.name) {
      ecoMapping[entry.eco] = entry.name; // Map ECO code to name
    }
  }
}

// Read all files from the input directory
fs.readdirSync(inputDir).forEach((file) => {
  // Process only .json files
  if (path.extname(file) === ".json") {
    const filePath = path.join(inputDir, file);
    console.log(`Processing file: ${filePath}`);
    processFile(filePath);
  }
});

// Write the consolidated mapping to the output file
fs.writeFileSync(outputFile, JSON.stringify(ecoMapping, null, 2));
console.log(`ECO mapping saved to ${outputFile}`);
