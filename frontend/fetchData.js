/* Main controller function */
// async function fetchData(inputID, statsID) {
//   const username = document.getElementById(inputID).value.trim();
//   if (!username) {
//     alert("You must enter a username");
//     return;
//   }
//   await fetchUserAPI(username, statsID);
//   await fetchGameAPI(username, statsID);

// }

let pyodideInstance;

// Function to load Pyodide and its required packages
async function loadPyodideAndPackages() {
  const pyodide = await loadPyodide(); // Initialize Pyodide
  console.log("Pyodide core loaded."); // Debugging
  await pyodide.loadPackage(['numpy', 'scikit-learn', 'joblib']); // Load necessary packages
  console.log("Packages loaded:", pyodide.loadedPackages); // Debugging
  pyodideInstance = pyodide; // Assign the instance
  console.log("Pyodide instance assigned:", pyodideInstance); // Debugging
}


// Call the function to initialize Pyodide
const pyodideReadyPromise = loadPyodideAndPackages();
pyodideReadyPromise
    .then(() => {
        console.log("Pyodide successfully initialized. Loading the model...");
        return loadModelFromJSON();
    })
    .then(() => {
        console.log("Model is ready for predictions.");
    })
    .catch((e) => {
        console.error("Error during Pyodide or model initialization:", e.message);
    });



async function fetchData(inputID, statsID) {
  const username = document.getElementById(inputID).value.trim();
  if (!username) {
      alert("You must enter a username");
      return;
  }

  await fetchUserAPI(username, statsID);
  await fetchGameAPI(username, statsID);

  // Collect stats for predictions
  const statsTableBody = document.getElementById(`${statsID}-table-body`);
  const stats = Array.from(statsTableBody.rows).map((row) => {
      const value = row.cells[1].textContent;
      return parseFloat(value) || 0; // Parse as float or use 0 as fallback
  });

  // Save stats globally for prediction
  if (statsID === "stats1") {
      window.user1Stats = stats;
  } else if (statsID === "stats2") {
      window.user2Stats = stats;
  }
}



function triggerPrediction() {
  if (window.user1Stats && window.user2Stats) {
      console.log("Triggering prediction with stats:", window.user1Stats, window.user2Stats);
      predictOutcome(window.user1Stats, window.user2Stats);
  } else {
      alert("Stats for both users are not yet loaded. Please fetch data for both users first.");
  }
}
async function predictOutcome(user1Stats, user2Stats) {
  if (!pyodideInstance) {
      alert("Pyodide is not yet ready. Please wait.");
      return;
  }

  try {
      // Convert JavaScript stats arrays to Python-compatible objects
      const user1StatsPy = pyodideInstance.toPy(user1Stats);
      const user2StatsPy = pyodideInstance.toPy(user2Stats);

      // Inject the data into Pyodide's Python environment
      pyodideInstance.globals.set("user1_stats", user1StatsPy);
      pyodideInstance.globals.set("user2_stats", user2StatsPy);

      // Execute the Python function
      const result = await pyodideInstance.runPythonAsync(`
        def predict_outcome(user1_stats, user2_stats):
          features = user1_stats + user2_stats
          prediction = model.predict([features])
          return prediction[0]

        # Call the function and return the result
        predict_outcome(user1_stats, user2_stats)
      `);

      console.log("Prediction result:", result);
      alert(`The predicted outcome is: ${result}`);
  } catch (e) {
      console.error("Error during prediction:", e);
  }
}









async function fetchUserAPI(username, statsID) {
  const USERURL = "https://lichess.org/api/user/" + username + "/perf/blitz";
  try {
    const response = await fetch(USERURL);
    if (response.status !== 200) {
      throw new Error(`Failed to fetch user data: ${response.status}`);
    }

    const data = await response.json();
    const rating = data?.perf?.glicko?.rating || "N/A";
    const deviation = data?.perf?.glicko?.deviation || "N/A";
    const totalGames = data?.stat?.count?.all || "N/A";

    // Extract the best wins
    const bestWins = data?.stat?.bestWins?.results || [];
    console.log(bestWins);
    let userBestWin1 = { opRating: "N/A", opponent: "N/A" };
    let userBestWin2 = { opRating: "N/A", opponent: "N/A" };
    let userBestWin3 = { opRating: "N/A", opponent: "N/A" };

    // Extract detailed info for the top 3 wins
    if (bestWins.length >= 3) {
      userBestWin1 = {
        opRating: bestWins[0]?.opRating || "N/A",
        opponent: bestWins[0]?.opId?.name || "Unknown" // Fallback to "Unknown" if opName is missing
      };
      userBestWin2 = {
        opRating: bestWins[1]?.opRating || "N/A",
        opponent: bestWins[1]?.opId?.name || "Unknown"
      };
      userBestWin3 = {
        opRating: bestWins[2]?.opRating || "N/A",
        opponent: bestWins[2]?.opId?.name || "Unknown"
      };
    }

    const tableBody = document.getElementById(`${statsID}-table-body`);
    tableBody.innerHTML = ""; // Clear previous data

    // Add rows to the table
    addTableRow(tableBody, "Blitz Rating", rating);
    addTableRow(tableBody, "Rating Deviation", deviation);
    addTableRow(tableBody, "Total Games Played", totalGames);
    addTableRow(
      tableBody,
      "Highest Rated Win",
      `${userBestWin1.opRating} vs ${userBestWin1.opponent}`
    );
    addTableRow(
      tableBody,
      "Second Highest Rated Win",
      `${userBestWin2.opRating} vs ${userBestWin2.opponent}`
    );
    addTableRow(
      tableBody,
      "Third Highest Rated Win",
      `${userBestWin3.opRating} vs ${userBestWin3.opponent}`
    );
  } catch (e) {
    console.error(e);
  }
}


// async function loadModel() {
//   // Wait for Pyodide to load
  
//   pyodideInstance = await pyodideReadyPromise;
//   if (!pyodideInstance) {
//     console.error("Pyodide is not yet initialized.");
//     return;
//   }
//   console.log("Pyodide initialized:", pyodideInstance);
//   console.log("Pyodide instance properties:", Object.keys(pyodideInstance));

//   console.log("Filesystem check:", pyodideInstance.FS);


//   // Fetch the model file
//   const response = await fetch('./model/best_random_forest.pkl');
//   if (!response.ok) {
//       console.error('Failed to fetch the .pkl file. Status:', response.status);
//       return;
//   }

//   const arrayBuffer = await response.arrayBuffer();
//     try {
//         pyodideInstance.FS.writeFile('/best_random_forest.pkl', new Uint8Array(arrayBuffer));
//         console.log('File written to Pyodide virtual filesystem:', pyodideInstance.FS.readdir('/'));
//     } catch (e) {
//         console.error('Error writing the model to Pyodide FS:', e);
//         return;
//     }


//   // Load the model in Python
//   const pythonCode = `
// import joblib

// # Load the model
// model = joblib.load('/best_random_forest.pkl')

// # Define the predict_outcome function
// def predict_outcome(user1_stats, user2_stats):
//     features = user1_stats + user2_stats
//     prediction = model.predict([features])
//     return prediction[0]
//   `;
//   try {
//       await pyodideInstance.runPythonAsync(pythonCode);
//       console.log('Random Forest model loaded successfully!');
//   } catch (e) {
//       console.error('Error loading the model in Pyodide:', e);
//   }
// }

// async function loadModel() {
//   try {
      
//       // Fetch the model file
//       const response = await fetch('./model/best_random_forest.pkl');
//       if (!response.ok) {
//           throw new Error(`Failed to fetch the .pkl file. Status: ${response.status}`);
//       }

//       const arrayBuffer = await response.arrayBuffer();
//       try {
//           pyodideInstance.FS.writeFile('/best_random_forest.pkl', new Uint8Array(arrayBuffer));
//           console.log('File written to Pyodide virtual filesystem:', pyodideInstance.FS.readdir('/'));
//           const files = pyodideInstance.FS.readdir('/');
//           if (!files.includes('best_random_forest.pkl')) {
//               throw new Error('Model file is missing from the Pyodide filesystem.');
//           }
//       } catch (e) {
//           throw new Error(`Error writing the model to Pyodide FS: ${e.message}`);
//       }

//       // Load model in Python
//       const pythonCode = `
//           import joblib

//           # Load the model
//           model = joblib.load('/best_random_forest.pkl')

//           # Define the predict_outcome function
//           def predict_outcome(user1_stats, user2_stats):
//               features = user1_stats + user2_stats
//               prediction = model.predict([features])
//               return prediction[0]
//       `;
//       try {
//           await pyodideInstance.runPythonAsync(pythonCode);
//           console.log('Random Forest model loaded successfully!');
//       } catch (e) {
//           throw new Error(`Error running Python code: ${e.message}`);
//       }
//   } catch (e) {
//       console.error('Error during model loading:', e.message);
//       throw e; // Propagate error for outer handling
//   }
// }

// Fetch and parse the JSON model
async function loadModelFromJSON() {
  // Fetch the JSON file
  const response = await fetch('./model/model.json');
  if (!response.ok) {
    throw new Error(`Failed to fetch the model JSON: ${response.status}`);
  }
  
  const arrayBuffer = await response.arrayBuffer();

  // Write the JSON file to Pyodide's virtual filesystem
  pyodideInstance.FS.writeFile('/model.json', new Uint8Array(arrayBuffer));
  console.log('Model JSON file written to Pyodide FS:', pyodideInstance.FS.readdir('/'));

  // Load and rebuild the model in Python
  await pyodideInstance.runPythonAsync(`
      import json
      import numpy as np
      from sklearn.ensemble import RandomForestClassifier

      # Load the JSON model into Python
      with open('/model.json', 'r') as f:
          model_data = json.load(f)

      # Rebuild the Random Forest model
      model = RandomForestClassifier(
          n_estimators=model_data["n_estimators"],
          max_depth=model_data["max_depth"],
          random_state=model_data["random_state"]
      )
      # Load parameters if needed (e.g., feature importances)
      model.n_features_in_ = len(model_data["feature_importances"])
      model.feature_importances = np.array(model_data["feature_importances"])
  `);

  console.log('Random Forest model rebuilt successfully in Pyodide.');
}






const ecoMapping = {
  "A00": "Ware Opening",
  "A01": "The Scientist's Method",
  "A02": "Bird Opening: Schlechter Gambit",
  "A03": "Bird: Lasker, 3...g6",
  "A04": "Reti: 1...c5",
  "A05": "Zukertort Opening: Quiet System",
  "A06": "Queen's Pawn Game, Symmetrical, 3.c4",
  "A07": "Reti: KIA, Yugoslav, Main Line, 6.Nbd2 e6",
  "A08": "Zukertort Opening: Grünfeld Reversed",
  "A09": "Réti Opening, proper:Advance Variation, Michel Gambit",
  "A10": "Réti Opening",
  "A11": "English: Caro-Kann Defence, 3.g3 Bg4",
  "A12": "Réti Opening: Anglo-Slav Variation, Torre System",
  "A13": "English: 1...e6 2.Nf3 Nf6",
  "A14": "Réti Opening: Anglo-Slav Variation, Bogoljubov Variation, Stonewall Line",
  "A15": "English Opening",
  "A16": "King's Indian Defence",
  "A17": "English: Nimzo-English, 4.Qc2 O-O",
  "A18": "English: Mikenas, French, 4.cxd5",
  "A19": "English: Mikenas, Sicilian, 4.e5",
  "A20": "English: King's, Nimzowitsch, 2...Nc6",
  "A21": "English: Lukin, 5.Ng5 Nf6",
  "A22": "English: King's, 2.Nc3 Nf6 3.Nf3 e4",
  "A23": "English: Bremen, Keres, 4.Nf3 e4",
  "A24": "English: Bremen, 3...g6",
  "A25": "English: Closed, Troeger, 5.d3",
  "A26": "English: Closed, 5.d3 d6 6.Rb1 f5",
  "A27": "English: Three Knights, 3...g6 4.d4 exd4 5.Nxd4",
  "A28": "English: Four Knights, 4.e3 Bb4 5.Qc2",
  "A29": "English: Four Knights, Main Line 6.O-O e4",
  "A30": "English: Symmetrical, 2.Nf3 Nc6",
  "A31": "English: Symmetrical, Two Knights, 4...Nc6",
  "A32": "English: Symmetrical, Two Knights, 5.Nc3 d5",
  "A33": "English: Symmetrical, Two Knights, 5.Nc3 Nc6 6.Ndb5 d5 Queenswap",
  "A34": "English: Symmetrical, 3 Knights, Queenswap",
  "A35": "English Opening, Symmetrical: Four Knights",
  "A36": "English: Symmetrical, Keres-Parma, Main Line Exchange",
  "A37": "English: Symmetrical, 5.Nf3 Nh6 6.O-O",
  "A38": "English: Symmetrical, Main Line, 7.Rb1",
  "A39": "English: Symmetrical, Main Line 7.d4, 9.Qxd4",
  "A40": "Borg Gambit",
  "A41": "Zukertort Opening: Wade Defense, Chigorin Plan",
  "A42": "Pterodactyl Defense: Central, Bogolubovia",
  "A43": "Queen's Pawn Game: Liedmann Gambit",
  "A44": "Old Benoni: Czech, 3.e4 d6 4.Nf3",
  "A45": "London System Main Line with Black ...e6 and ...c5",
  "A46": "Indian Defence, Knights Variation",
  "A47": "Pseudo Queen's Indian Defense",
  "A48": "Torre Attack: Fianchetto Defense, Euwe Variation",
  "A49": "Neo-King's Indian: Fianchetto System",
  "A50": "Black Knights Tango",
  "A51": "Indian Defense: Budapest Defense, Fajarowicz-Steiner Variation",
  "A52": "Budapest: 3...Ng4 4.e3",
  "A53": "Old Indian Defence",
  "A54": "Old Indian: 5.g3 g6",
  "A55": "Old Indian: Main Line, 8.Re1 Re8",
  "A56": "Vulture Defense",
  "A57": "Benko Gambit: Zaitsev, 8.Nf3",
  "A58": "Benko Gambit: Nd2 Variation",
  "A59": "Benko Gambit: 7.e4, Main Line, 11...Nbd7 12.Re1 Qa5",
  "A60": "Benoni: Snake, 6.Nf3 Bc7",
  "A61": "Benoni: Uhlmann, 7...h6",
  "A62": "Benoni: Fianchetto, 9.O-O Re8",
  "A63": "Benoni: Fianchetto, 9...Nbd7 10.Nd2 Re8",
  "A64": "Benoni: Fianchetto, 11...Re8 12.Nc4 Ne5",
  "A65": "Benoni: Saemisch, 8.Nge2",
  "A66": "Benoni: Mikenas Attack, 9.Nb5 dxe5 10.Nd6+ Ke7 11.Nxc8+ Qxc8 12.Nf3",
  "A67": "Benoni: Four Pawns, Taimanov, 9.Bd3 O-O 10.Nf3 Na6",
  "A68": "Benoni: Four Pawns, 9.Be2 Bg4 10.O-O Nbd7 11.h3 Bxf3 12.Bxf3 Re8 13.Re1",
  "A69": "Benoni: Four Pawns, Main Line, 10.O-O",
  "A70": "Benoni: Classical, 8.Qa4+ Bd7 9.Qb3 Qc7",
  "A71": "Benoni: Classical, 8.Bg5 h6 9.Bh4 g5",
  "A72": "Benoni: Classical, 8.Be2 O-O 9.Nd2",
  "A73": "Benoni: Classical, 9.O-O Nbd7",
  "A74": "Benoni: Classical, 9.O-O a6 10.a4 Nbd7 11.Nd2",
  "A75": "Benoni: Classical, 9.O-O a6 10.a4 Bg4 11.Nd2",
  "A76": "Benoni: Classical, Main Line, 10.Qc2 Na6 11.Re1 Bg4",
  "A77": "Benoni: Classical, Main Line, 10.Nd2 Nbd7 11.a4 Ne5 12.Re1",
  "A78": "Benoni: Classical, Main Line, 10.Nd2 Na6 11.Re1",
  "A79": "Benoni: Classical, Main Line, 10.Nd2 Na6 11.f3 Nc7 12.a4 Nd7",
  "A80": "Dutch Defense: 2. Bg5",
  "A81": "Dutch Leningrad",
  "A82": "Rat Defense: Balogh Defense",
  "A83": "Dutch: Staunton Gambit, 4.Bg5 Nc6 5.f3",
  "A84": "Bladel Attack, Main Line",
  "A85": "Dutch: 2.c4 Nf6 3.Nc3 g6 4.Nf3 Bg7 5.e3",
  "A86": "Dutch: Leningrad, 4.Nf3 Bg7 5.Nc3",
  "A87": "Dutch: Leningrad, Main Line, 7.Nc3 Qe8 8.Re1",
  "A88": "Dutch: Leningrad, Main Line, 7.Nc3 c6 8.Re1",
  "A89": "Dutch: Leningrad, Main Line, 7.Nc3 Nc6 8.d5 Ne5 9.Nxe5 dxe5 10.Qb3",
  "A90": "Dutch: Dutch-Indian, 5.Nd2",
  "A91": "Dutch: Botvinnik-Bronstein Variation",
  "A92": "Dutch: Stonewall, 7.Qc2 c6 8.Nbd2",
  "A93": "Dutch: Stonewall, Botvinnik, 8.Qc2 Ne4",
  "A94": "Dutch: Stonewall, Botvinnik, 8.Ba3 Nbd7 9.Bxe7",
  "A95": "Dutch: Stonewall, 7.Nc3 c6 8.Qc2",
  "A96": "Dutch: Classical, 7.Nc3 a5 8.Re1",
  "A97": "Dutch: Ilyin-Zhenevsky, Winter, 8...Qh5",
  "A98": "Dutch: Ilyin-Zhenevsky, 8.Qc2 Qh5",
  "A99": "Dutch: Ilyin-Zhenevsky, 8.b3 Qh5 9.Bb2",
  "B00": "Owen Defense: Matovinsky Gambit Accepted",
  "B01": "Queen's Pawn Game",
  "B02": "Alekhine Defence:Krejcik Variation",
  "B03": "Alekhine: Four Pawns Attack, Fahrni Variation",
  "B04": "Alekhine: Modern, Larsen, 5.Nxe5 g6 6.Bc4 c6 7.O-O",
  "B05": "Alekhine: Modern, Main Line, 8.Nc3 O-O 9.Be3 Nc6 10.exd6 cxd6",
  "B06": "Rat Defense: Accelerated Gurgenidze",
  "B07": "Pirc/Reti: Wade Defence",
  "B08": "Pirc: Classical, Spassky System, 6...d5",
  "B09": "Pirc: Austrian, 5...c5 6.dxc5",
  "B10": "Hillbilly Attack, Schaeffer Gambit",
  "B11": "Caro-Kann: Two Knights, 3...Bg4 4.h3 Bxf3 5.Qxf3 Nf6",
  "B12": "Caro-Kann: Advance, 4.Nf3 e6 5.Be2 Nd7",
  "B13": "Caro-Kann Exchange Variation, Rubinstein, 7.Qb3 Qd7",
  "B14": "Caro-Kann: Panov-Botvinnik, 5...g6, Main Line, 8.Be2 Nbd7",
  "B15": "Caro-Kann: 4.Nxe4 Nf6",
  "B16": "Caro-Kann: Bronstein-Larsen, 6.Qd3",
  "B17": "Caro-Kann Defense: Karpov Variation, Modern Variation",
  "B18": "Caro-Kann Defence:Burris Gambit accepted",
  "B19": "Caro-Kann Defence:Classical Variation, Spassky, 10.Qxd3 e6",
  "B20": "Sicilian Defense: Mengarini Variation",
  "B21": "Smith-Morra Gambit",
  "B22": "Sicilian: Alapin, 2...Nf6, 5.Qxd4",
  "B23": "Sicilian: Closed, Grand Prix, 3...g6 4.Nf3 Bg7 5.Bc4 e6",
  "B24": "Sicilian: Closed, 3.g3 g6, 5.Nge2",
  "B25": "Sicilian: Closed, 6.f4 Rb8",
  "B26": "Sicilian: Closed, 6.Be3 Rb8 7.Qd2 b5 8.Nge2",
  "B27": "Sicilian Defense: Jalalabad Variation",
  "B28": "Sicilian: O'Kelly, 3.d4 cxd4 4.Nxd4 Nf6",
  "B29": "Sicilian: Nimzowitsch, Rubinstein Countergambit, 7.dxc5",
  "B30": "Sicilian Defense: Nyezhmetdinov-Rossolimo Attack: 3...a6?!",
  "B31": "Sicilian: Rossolimo, 3...g6 4.O-O Bg7 5.Re1 Nf6 6.c3 O-O 7.h3",
  "B32": "Sicilian: Open, 2...Nc6, 4...d6",
  "B33": "Classical Sicilian Richter Rauser variation",
  "B34": "Sicilian: Accelerated Fianchetto, Modern, 6.Nde2",
  "B35": "Sicilian: Accelerated Fianchetto, Modern, 7.Bc4 Qa5 8.O-O O-O 9.Bb3 d6 10.h3 Bd7 11.f4",
  "B36": "Sicilian: Maroczy Bind, 5...Nf6 6.Nc3 Nxd4",
  "B37": "Sicilian: Maroczy Bind, 6.Nc2 Nf6 7.Nc3 O-O",
  "B38": "Sicilian: Maroczy Bind, 7.Nc3 O-O 8.Be2 d6 9.O-O Nxd4",
  "B39": "Sicilian: Maroczy Bind, Breyer, 8.Qxg4 Nxd4 9.Qd1 Ne6 10.Rc1 Qa5 11.Qd2",
  "B40": "Sicilian, Kan, 5.Nc3",
  "B41": "Sicilian: Kan, 5.g3",
  "B42": "Sicilian: Kan, Polugaevsky, 6.Nb3 Ba7",
  "B43": "Sicilian: Kan, 5.Nc3 Qc7 6.g3 Nf6",
  "B44": "Sicilian: Taimanov, Szen, Hedgehog, 11.Be3 Ne5",
  "B45": "Sicilian: Taimanov, Four Knights, 6.Nxc6 bxc6 7.e5 Nd5 8.Ne4 Qc7",
  "B46": "Sicilian: Taimanov, 5...a6 6.Nxc6 bxc6 7.Bd3 d5",
  "B47": "Sicilian: Taimanov, 6.Nxc6",
  "B48": "Sicilian: Taimanov, 6.Be3 Nf6",
  "B49": "Sicilian: Taimanov, 6.Be3 a6 7.Be2 Nge7",
  "B50": "Sicilian Defense: Modern Variations, Anti-Qxd4 Move Order",
  "B51": "Sicilian Canal-Sokolsky (Rossolimo) Attack",
  "B52": "Sicilian: Moscow 3...Bd7 4.Bxd7+ Qxd7",
  "B53": "Sicilian, Chekhover, Main Line, 11.Qd2",
  "B54": "Sicilian: Prins (Moscow), 5...Nc6 6.c4 Qb6",
  "B55": "Sicilian: Prins, Venice Attack, 6...Nbd7 7.Nf5 d5",
  "B56": "Open Sicilian 5...e5 6. Bb5+ Nbd7",
  "B57": "Sicilian: Sozin, Benko, 7.Nxc6 bxc6 8.O-O g6",
  "B58": "Sicilian: Boleslavsky, Louma Variation",
  "B59": "Sicilian: Boleslavsky, 7.Nb3 Be7 8.O-O O-O 9.Kh1",
  "B60": "Sicilian: Richter-Rauzer, Larsen, 7.Nb3",
  "B61": "Sicilian: Richter-Rauzer, Larsen, Main Line, 10.f4",
  "B62": "Sicilian: Richter-Rauzer, Margate, 7...Bd7 8.Bxc6",
  "B63": "Sicilian: Richter-Rauzer, Podebrad, 10.f3 Rd8 11.Kb1",
  "B64": "Sicilian: Richter-Rauzer, 7.Qd2 Be7, 9.f4 h6 10.Bh4 e5",
  "B65": "Sicilian: Richter-Rauzer, 7...Be7, 9.f4 Nxd4 10.Qxd4 Qa5 11.Kb1",
  "B66": "Sicilian: Richter-Rauzer, 7...a6 8.O-O-O Nxd4 9.Qxd4 Be7",
  "B67": "Sicilian: Richter-Rauzer, 7...a6, 9.f4 h6 10.Bh4 g5",
  "B68": "Sicilian: Richter-Rauzer, 7...a6, 9.f4 Be7 10.Nf3 b5 11.e5",
  "B69": "Sicilian: Richter-Rauzer, 7...a6, 9.f4 Be7 10.Nf3 b5 11.Bxf6 gxf6 12.Kb1",
  "B70": "Sicilian: Dragon, 6.g3 Nc6 7.Nde2",
  "B71": "Sicilian: Dragon, Levenfish, 6...Nc6 7.Nxc6",
  "B72": "Sicilian Defense: Dragon Variation: 7. Ng4??",
  "B73": "Sicilian: Dragon, Classical, 9.Kh1",
  "B74": "Sicilian: Dragon, Classical, 9.Nb3 Be6 10.f4 Rc8",
  "B75": "Sicilian: Dragon, Yugoslav, 7...Nc6 8.Qd2 Bd7 9.O-O-O Rc8",
  "B76": "Sicilian: Dragon, Yugoslav, 9.O-O-O Nxd4: 11.Kb1 Qc7 12.g4",
  "B77": "Sicilian: Dragon, Yugoslav, 9.Bc4 Nxd4",
  "B78": "Sicilian: Dragon, Yugoslav, Old Main Line, 11.Bb3 Rfc8",
  "B79": "Sicilian: Dragon, Yugoslav, Old Main Line, 12.h4 Ne5 13.Kb1 Nc4",
  "B80": "Sicilian: Scheveningen, Vitolins, 6...Bd7",
  "B81": "Sicilian: Scheveningen, Keres, Perenyi Attack, 7...h6 8.f4",
  "B82": "Sicilian: Scheveningen, Tal, 8...Qc7",
  "B83": "Sicilian: Scheveningen, Modern, 9.f4 e5 10.Nb3 exf4 11.Bxf4",
  "B84": "Sicilian: Scheveningen, Classical, 7.O-O Qc7 8.Kh1 Nc6",
  "B85": "Sicilian: Scheveningen, Classical, Main Line, 9...Qc7",
  "B86": "Sicilian: Sozin-Scheveningen, 6...Qb6",
  "B87": "Sicilian: Sozin-Najdorf, 7.Bb3 b5 8.O-O Be7 9.Qf3",
  "B88": "Sicilian: Sozin-Scheveningen, 7.O-O",
  "B89": "Sicilian: Velimirovic, 9.O-O-O Qc7 10.Bb3 a6",
  "B90": "Najdorf Sicilian, English Attack",
  "B91": "Sicilian: Najdorf, 6.g3 Nc6",
  "B92": "Sicilian: Najdorf, 6.Be2 Nbd7",
  "B93": "Sicilian: Najdorf, 6.f4 Qc7 7.Nf3 Nbd7 8.Bd3",
  "B94": "Sicilian: Najdorf, 6.Bg5 Nbd7 7.f4 b5",
  "B95": "Sicilian: Najdorf, 6...e6 7.Qf3 Nbd7",
  "B96": "Polugaevsky Variation",
  "B97": "Sicilian: Najdorf, Poisoned Pawn, Main Line, Timman's 13.Be2",
  "B98": "Sicilian: Najdorf, Gothenburg, 11.Qh5",
  "B99": "Sicilian: Najdorf, Modern Main Line 13.f5 Nc5 14.h4",
  "C00": "Chigorin Variation, 3...Nc6",
  "C01": "French Defense, Exchange Variation: 4.Be3",
  "C02": "French Defense: Advance Variation, Milner-Barry Gambit",
  "C03": "French: Tarrasch, Guimard, 4.Ngf3",
  "C04": "French: Tarrasch, Guimard, Main Line, 6.Nb3 Be7",
  "C05": "French Defence: Tarrasch Variation / 3....Nf6",
  "C06": "French: Tarrasch, Closed, Leningrad, 9.O-O Bd7",
  "C07": "French: Tarrasch, Open, 4.Ngf3 Nf6",
  "C08": "French: Tarrasch, Open, 4.exd5 exd5 5.Ngf3 Nf6, Main Line, 10.Nb3",
  "C09": "French: Tarrasch, Open, Main Line, 9.Nb3 Bd6 10.Re1 O-O 11.Bg5 Bg4",
  "C10": "Sicilian Defense: Marshall Gambit",
  "C11": "Classical Defence/Steinitz Variation",
  "C12": "French: MacCutcheon, Main Line, 11.Nf3 Nc6",
  "C13": "French: Classical, Tartakower, 6.Bxe7",
  "C14": "French: Classical, Steinitz, 9.Qd2 Nc6 10.dxc5 Qxc5",
  "C15": "French: Winawer, Winkelmann-Reimer, Huebner Defence",
  "C16": "French: Winawer, Petrosian, 5.Bd2",
  "C17": "French: Winawer, Swiss, 6.b4 cxd4 7.Qg4 Ne7 8.bxa5",
  "C18": "French: Winawer, Poisoned Pawn, Main Line, 13.Nxc3",
  "C19": "French: Winawer, Smyslov, 7...Qa5",
  "C20": "Parham Attack/Scholar's Mate",
  "C21": "Danish Gambit Accepted, Classical Defence",
  "C22": "Center Game: Paulsen Attack Variation",
  "C23": "Bishop's Opening: Boi Variation",
  "C24": "Bishop's Opening: Walkerling, Main Line",
  "C25": "Vienna Game, Max Lange Defence (transpose from Nimzowitsch)",
  "C26": "Vienna: Smyslov, 3...Nc6",
  "C27": "Vienna Game, Falkbeer Defence",
  "C28": "Vienna: 3.Bc4 Nc6 4.f4",
  "C29": "Vienna Game, Würzburger Trap",
  "C30": "King's Gambit Declined",
  "C31": "Van Geet Opening: Grünfeld Defense, Steiner Gambit",
  "C32": "King's Gambit Declined: Falkbeer Countergambit, Tarrasch Variation",
  "C33": "King's Bishop Gambit Accepted",
  "C34": "King's Gambit Accepted: Wagenbach Defense",
  "C35": "King's Gambit Accepted: Cunningham Defense",
  "C36": "King's Gambit Accepted: Modern Defense",
  "C37": "King's Gambit Accepted, Salvio Gambit",
  "C38": "King's Gambit Accepted: Traditional Variation",
  "C39": "King's Gambit Accepted: Kieseritzky Gambit, Kolisch Defense",
  "C40": "Gunderam Gambit, Bishop Attack, Main Line, Exchange Line",
  "C41": "Philidor Defense: 3...Nc6",
  "C42": "Petrov Defense: Stafford Gambit",
  "C43": "Russian Game: Modern Attack, Trifunovic Variation",
  "C44": "Irish Gambit Accepted",
  "C45": "Scotch: Steinitz, Berger Variation",
  "C46": "Three Knights: Steinitz, 4.d4 exd4 5.Nxd4 Bg7 6.Be3 Nf6",
  "C47": " Halloween Gambit Accepted",
  "C48": "Four Knights: Spanish, Classical, Marshall Variation",
  "C49": "Four Knights: Symmetrical, Metger, 10.d4 Ne6 11.Bc1 Rd8",
  "C50": "Italian Game: Blackburne-Kostić Gambit",
  "C51": "Italian Game: Evans Gambit, Ulvestad Variation",
  "C52": "Italian Game: Evans Gambit, Waller Attack",
  "C53": "talian Game: Classical Variation, Center Attack",
  "C54": "Italian Game: Giuoco Piano, Therkatz-Herzog Variation",
  "C55": "Two Knights Defence",
  "C56": "Scotch Gambit: Nakhmanson Gambit, Kf6 Defence, Rook  Attack",
  "C57": "Two Knights Defense, Traxler Counterattack, Bishop Sacrifice Line",
  "C58": "Two Knights Defence: Morphy, Polerio, 6...Bd7",
  "C59": "Two Knights Defence, Main Line, 11.d4 exd3",
  "C60": "Ruy Lopez - 4_d4!?",
  "C61": "Spanish: Bird's, 5.O-O c6 6.Bc4",
  "C62": "Ruy Lopez: Steinitz Defence",
  "C63": "Ruy Lopez: Schliemann Defense, Möhring Variation",
  "C64": "Spanish: Classical, Exchange",
  "C65": "Spanish: Berlin, Beverwijk, 5.Nxe5",
  "C66": "Spanish: Closed Berlin, Tarrasch Trap",
  "C67": "Spanish: Open Berlin, Main Line 9.Nc3 (Rio de Janerio)",
  "C68": "Ruy Lopez: Exchange Variation",
  "C69": "Spanish: Exchange, Gligoric, 8.Ne2",
  "C70": "Ruy Lopez: Morphy Defense, Classical Defense Deferred",
  "C71": "Spanish: Modern Steinitz, 5.d4",
  "C72": "Spanish: Modern Steinitz, 5.O-O Ne7",
  "C73": "Spanish: Modern Steinitz, Richter Variation",
  "C74": "Spanish: Modern Steinitz, Siesta, Kopayev, Main Line",
  "C75": "Spanish: Modern Steinitz, Rubinstein, 7.Be3",
  "C76": "Spanish: Modern Steinitz, Bronstein, 7.O-O Bg7 8.Re1",
  "C77": "Ruy Lopez, Anderssen Variation: 5...b5",
  "C78": "Spanish: Moeller Defence, 6.Nxe5",
  "C79": "Spanish: Steinitz Deferred, Exchange",
  "C80": "Ruy Lopez, Riga Variation, Main Line",
  "C81": "Spanish: Open, Keres, 10.Rd1 O-O 11.c4 bxc4 12.Bxc4 Bc5",
  "C82": "Spanish: Open, St. Petersburg, 11.Bc2 f5",
  "C83": "Spanish: Open, Classical, 10.Re1",
  "C84": "Spanish: Closed, Centre Attack, 7.Re1 O-O 8.e5 Ne8 9.c3",
  "C85": "Spanish: Closed, Exchange, 7.Qe2",
  "C86": "Spanish: Worrall Attack, 7...O-O 8.c3 d6 9.Rd1",
  "C87": "Spanish: Closed, Averbakh, 7.c3 O-O 8.h3 Bd7",
  "C88": "Spanish: Closed, Anti-Marshall 8.a4 Bb7 9.d3 d6 10.Nc3",
  "C89": "Ruy Lopez, Marshall Gambit with 15. Re4",
  "C90": "Spanish: Closed, Pilnik, 9...Na5",
  "C91": "Spanish: Closed, Bogoljubow, 10.d5 Na5 11.Bc2 Qc8",
  "C92": "Ruy Lopez, Zaitsev Variation",
  "C93": "Spanish: Closed, Smyslov, 12.Nf1 Bd7 13.Ng3 Na5 14.Bc2 c5",
  "C94": "Spanish: Closed, Breyer, Matulovic Variation",
  "C95": "Spanish: Closed, Breyer, Main Line, 15.a4 c5 16.d5 c4",
  "C96": "Spanish: Closed, Chigorin, Keres, 11.Nbd2 cxd4",
  "C97": "Spanish: Closed, Chigorin, 12...Re8",
  "C98": "Spanish: Closed, Chigorin, Rauzer, 14.Nf1 Be6",
  "C99": "Spanish: Closed, Chigorin, 13...Rd8",
  "D00": "Blackmar-Diemer Gambit (BDG)",
  "D01": "Richter-Veresov: 3...Ne4",
  "D02": "Queen's Pawn Game: Krause Variation",
  "D03": "Torre Attack",
  "D04": "Queen's Pawn Game: Colle System, Grünfeld Formation",
  "D05": "Rubinstein Opening: Semi-Slav Defense",
  "D06": "Austrian Defense",
  "D07": "Queen's Gambit Declined: Chigorin Defense, Tartakower Gambit",
  "D08": "Queen's Gambit Declined: Albin Countergambit, Tartakower Defense",
  "D09": "Queen's Gambit Declined: Albin Countergambit, Fianchetto Variation, Bg4 Line",
  "D10": "Slav: Winawer Countergambit, 4.cxd5 cxd5 5.Nf3",
  "D11": "Slav: Slav-Reti with b3",
  "D12": "Slav: 4.e3 Bf5 5.Qb3",
  "D13": "Slav: Exchange, 6.Bf4 e6 7.e3 Be7",
  "D14": "Slav: Exchange, 8.Qb3",
  "D15": "Slav: Geller Gambit, Spassky Variation",
  "D16": "Slav: Smyslov, 6.Ne5",
  "D17": "Slav: Czech, 6.Nh4 e6 7.Nxf5 exf5 8.e3",
  "D18": "Slav: Dutch, 8...O-O 9.Qb3",
  "D19": "Slav: Dutch, 8...O-O 9.Qe2 Ne4",
  "D20": "Queen's Gambit Accepted: Schwartz Defense",
  "D21": "Queen's Gambit Accepted: Slav Gambit",
  "D22": "Queen's Gambit Accepted: Alekhine Defense, Haberditz Variation",
  "D23": "Queen's Gambit Accepted: Mannheim Variation",
  "D24": "Queen's Gambit Accepted: Showalter Variation",
  "D25": "Queen's Gambit Accepted: Winawer Defense",
  "D26": "Queen's Gambit Accepted: Normal Variation, Traditional System",
  "D27": "Queen's Gambit Accepted: Furman Variation",
  "D28": "Queen's Gambit Accepted: Classical, Flohr Variation",
  "D29": "Queen's Gambit Accepted: Classical Defense, Alekhine System, Smyslov Variation",
  "D30": "Queen's Gambit Declined",
  "D31": "Queen's Gambit Declined, Queen's Knight Variation",
  "D32": "Tarrasch Defense: von Hennig Gambit",
  "D33": "Tarrasch Defense: Wagner Variation",
  "D34": "Tarrasch Defense: Prague Variation, Main Line",
  "D35": "Queen's Gambit Declined: Normal Defense",
  "D36": "Queen's Gambit Declined: Exchange Variation, Reshevsky Variation",
  "D37": "Queen's Gambit Declined: Vienna Variation, Quiet Variation",
  "D38": "Queen's Gambit Declined: Westphalian Variation",
  "D39": "Queen's Gambit Declined: Ragozin Defense, Vienna Variation",
  "D40": "Queen's Gambit Declined: Semi-Tarrasch Defense, Symmetrical Variation",
  "D41": "Queen's Gambit Declined: Semi-Tarrasch Defense, San Sebastian Variation",
  "D42": "Queen's Gambit Declined: Semi-Tarrasch Defense, Main Line",
  "D43": "Semi-Slav: Moscow, Main Line, 11.Rc1",
  "D44": "Semi-Slav: Botvinnik, Main Line, 12.g3 c5 13.d5 Qb6",
  "D45": "Semi-Slav: 6.Qc2 Be7",
  "D46": "Semi-Slav: Romih, 7.O-O O-O",
  "D47": "Semi-Slav: Meran, Wade, Main Line, 12.O-O",
  "D48": "Semi-Slav: Meran, Reynolds, 10...Qc7",
  "D49": "Semi-Slav: Meran, Trifunovic Variation",
  "D50": "Queen's Gambit Declined: Semi-Tarrasch Defense, Krause Variation",
  "D51": "Queen's Gambit Declined: Rochlin Variation",
  "D52": "Queen's Gambit Declined: Cambridge Springs Defense, Yugoslav Variation",
  "D53": "Queen's Gambit Declined: Modern Variation, Heral Variation",
  "D54": "Queen's Gambit Declined: Neo-Orthodox Variation",
  "D55": "Queen's Gambit Declined: Pillsbury Attack",
  "D56": "Queen's Gambit Declined: Lasker Defense, Teichmann Variation",
  "D57": "Queen's Gambit Declined: Lasker Defense, Main Line",
  "D58": "Queen's Gambit Declined: Tartakower Defense, Exchange Variation",
  "D59": "Queen's Gambit Declined: Tartakower Defense, Makogonov Exchange Variation",
  "D60": "Queen's Gambit Declined: Orthodox Defense, Rauzer Variation",
  "D61": "Queen's Gambit Declined: Orthodox Defense, Rubinstein Variation",
  "D62": "Queen's Gambit Declined: Orthodox Defense, Rubinstein Variation, Flohr Line",
  "D63": "Queen's Gambit Declined: Orthodox Defense, Swiss, Karlsbad Variation",
  "D64": "Queen's Gambit Declined: Orthodox Defense, Rubinstein Attack",
  "D65": "Queen's Gambit Declined: Orthodox Defense, Rubinstein Attack",
  "D66": "Queen's Gambit Declined: Orthodox Defense, Fianchetto Variation",
  "D67": "Queen's Gambit Declined: Orthodox Defense, Main Line",
  "D68": "Queen's Gambit Declined: Orthodox Defense, Classical Variation",
  "D69": "Queen's Gambit Declined: Orthodox Defense, Classical Variation",
  "D70": "Neo-Grünfeld Defense: with Nf3",
  "D71": "Neo-Grünfeld Defense: Exchange Variation",
  "D72": "Neo-Gruenfeld, 5.cxd5 Nxd5 6.e4 Nb6 7.Ne2 O-O 8.O-O",
  "D73": "Neo-Gruenfeld, 6.Qb3",
  "D74": "Neo-Grünfeld Defense: Delayed Exchange Variation",
  "D75": "Neo-Grünfeld Defense: Delayed Exchange Variation",
  "D76": "Neo-Grünfeld Defense: Delayed Exchange Variation",
  "D77": "Neo-Grünfeld Defense: Classical Variation, Polgar Variation",
  "D78": "Neo-Grünfeld Defense: Classical Variation, Original Defense",
  "D79": "Neo-Grünfeld Defense: Ultra-Delayed Exchange Variation",
  "D80": "Grünfeld Defense: Zaitsev Gambit",
  "D81": "Grünfeld Defense: Russian Variation, Accelerated Variation",
  "D82": "Grünfeld Defense: Brinckmann Attack",
  "D83": "Grünfeld Defense: Brinckmann Attack, Reshevsky Gambit",
  "D84": "Grünfeld Defense: Brinckmann Attack, Grünfeld Gambit Accepted",
  "D85": "Grunfeld Exchange, 6.bxc3",
  "D86": "Grünfeld Defense: Exchange Variation, Simagin's Lesser Variation",
  "D87": "Grünfeld Defense: Exchange Variation, Spassky Variation",
  "D88": "Grünfeld Defense: Exchange Variation, Spassky Variation",
  "D89": "Grünfeld Defense: Exchange Variation, Spassky Variation",
  "D90": "Grünfeld Defense: Three Knights Variation",
  "D91": "Grünfeld Defense: Three Knights Variation, Petrosian System",
  "D92": "Grünfeld Defense: Three Knights Variation, Hungarian Attack",
  "D93": "Grünfeld Defense: Three Knights Variation, Hungarian Variation",
  "D94": "Grünfeld Defense: Three Knights Variation, Paris Variation",
  "D95": "Grünfeld Defense: Three Knights Variation, Vienna Variation",
  "D96": "Grünfeld Defense: Russian Variation",
  "D97": "Grünfeld Defense: Russian Variation, Szabo Variation",
  "D98": "Grünfeld Defense: Russian Variation, Smyslov Variation",
  "D99": "Grünfeld Defense: Russian Variation, Yugoslav Variation",
  "E00": "Queen's Pawn: Neo-Indian, 3...c5",
  "E01": "Catalan: 4...c6 5.Qc2",
  "E02": "Catalan: Open, 5.Qa4+ Nbd7 6.Nf3 a6 7.Nc3",
  "E03": "Catalan: Open, 5.Qa4+ Nbd7 6.Qxc4 c5 7.Nf3 a6 8.Qc2 b6",
  "E04": "Catalan: Open, 5.Nf3 Nc6 6.Qa4 Bb4+ 7.Bd2 Nd5",
  "E05": "Catalan: Open, Classical, 8.Qxc4, 10.Bg5",
  "E06": "Catalan: Closed, 6.Qc2",
  "E07": "Catalan: Closed, 6...Nbd7 7.Qd3",
  "E08": "Catalan: Closed, 7.Qc2 c6 8.Rd1 b6",
  "E09": "Catalan: Closed, Main Line, 9.e4 dxe4 10.Nxe4 Nxe4 11.Qxe4",
  "E10": "Catalan Opening",
  "E11": "Bogo-Indian: Vitolins, 6.g3",
  "E12": "Queen's Indian: Petrosian, Kasparov, 7...Nxc3 8.bxc3 c5 9.e4",
  "E13": "Queen's Indian: 5.Bg5 h6 6.Bh4 Bb4 7.Qc2 g5",
  "E14": "Queen's Indian: Dreev Variation",
  "E15": "Queen's Indian: Nimzowitsch, 5.Qc2",
  "E16": "Queen's Indian: Capablanca, Yates, 7.O-O O-O",
  "E17": "Queen's Indian: Pomar, Polugaevsky, 8...c6 9.cxd5 Nxd5 10.Nf5 Nc7 11.e4",
  "E18": "Queen's Indian: Old Main Line, 8.Qc2 Nxc3 9.bxc3",
  "E19": "Queen's Indian: Old Main Line, 9.Qxc3 f5 10.Rd1",
  "E20": "Nimzo-Indian: Romanishin, 8.cxd5",
  "E21": "Nimzo-Indian: Three Knights, 4...O-O",
  "E22": "Nimzo-Indian: Spielmann, 4...Nc6",
  "E23": "Nimzo-Indian: Spielmann, 4...c5 5.dxc5 Nc6 6.Nf3 Ne4",
  "E24": "Nimzo-Indian: Sämisch Variation",
  "E25": "Nimzo-Indian: Saemisch, Keres, Romanovsky, 9.Nh3",
  "E26": "Nimzo-Indian: Saemisch, 5...c5 6.e3 Qa5",
  "E27": "Nimzo-Indian: Saemisch, 5...O-O 6.f3 d5 7.e3",
  "E28": "Nimzo-Indian: Saemisch, 5...O-O 6.e3 c5 7.Ne2",
  "E29": "Nimzo-Indian: Saemisch, Capablanca, 10.O-O",
  "E30": "Nimzo-Indian: Leningrad, 6.d5 exd5",
  "E31": "Nimzo-Indian: Leningrad, Main Line, 8...Qe7",
  "E32": "Nimzo-Indian: Classical, 4...O-O 5.Nf3",
  "E33": "Nimzo-Indian: Classical, Milner-Barry (Zurich), 6.Bd2 O-O",
  "E34": "Nimzo-Indian: Classical, Noa, Queenswap",
  "E35": "Nimzo-Indian: Classical, Noa, Exchange, 6.Bg5 h6 7.Bxf6",
  "E36": "Nimzo-Indian: Classical, Noa, 5.a3 Bxc3+ 6.Qxc3 O-O",
  "E37": "Nimzo-Indian: Classical, Noa, Main Line, 7.Qc2 Nc6",
  "E38": "Nimzo-Indian: Classical, 4...c5 5.Nf3",
  "E39": "Nimzo-Indian: Classical, Pirc, 6.Nf3 Na6 7.g3",
  "E40": "Nimzo-Indian: Taimanov, 5.Ne2 d5",
  "E41": "Nimzo-Indian: Huebner, 8.O-O e5 9.Nd2",
  "E42": "Nimzo-Indian: 4.e3 c5 5.Ne2 d5",
  "E43": "Nimzo-Indian: Nimzowitsch, Keene Variation",
  "E44": "Nimzo-Indian: Nimzowitsch, 5.Ne2 Ne4 6.Qc2",
  "E45": "Nimzo-Indian: Nimzowitsch, 5.Ne2 Ba6 6.Ng3 h5",
  "E46": "Nimzo-Indian: Reshevsky, 6.a3 Be7 7.cxd5 exd5",
  "E47": "Nimzo-Indian: 4.e3 O-O 5.Bd3 d6",
  "E48": "Nimzo-Indian: 4.e3 O-O 5.Bd3 d5 6.Ne2 c5 7.O-O cxd4 8.exd4",
  "E49": "Nimzo-Indian: Botvinnik, 7...dxc4 8.Bxc4 c5 9.Ne2",
  "E50": "Nimzo-Indian: 4.e3 O-O 5.Nf3 Ne4",
  "E51": "Nimzo-Indian: 4.e3 O-O 5.Nf3 d5 6.Be2",
  "E52": "Nimzo-Indian: Main Line, 6...b6 7.O-O Bb7 8.cxd5 exd5 9.Ne5",
  "E53": "Nimzo-Indian: Main Line, Keres, 8.cxd5 exd5",
  "E54": "Nimzo-Indian: Main Line, Karpov, 10.Bg5 Bb7 11.Re1",
  "E55": "Nimzo-Indian: Main Line, Bronstein, 9.Qe2 b6 10.Rd1",
  "E56": "Nimzo-Indian: Main Line, 7...Nc6 8.cxd5",
  "E57": "Nimzo-Indian: Main Line, 8...dxc4 9.Bxc4 cxd4 10.exd4 Be7 11.Re1 a6",
  "E58": "Nimzo-Indian: Main Line, 9.bxc3 Qc7 10.Qc2",
  "E59": "Nimzo-Indian: Main Line, 9.bxc3 dxc4 10.Bxc4 Qc7 11.Qe2",
  "E60": "King's Indian Defense: Normal Variation, King's Knight Variation",
  "E61": "King's Indian: Smyslov System, 6.e3 c6",
  "E62": "King's Indian: Fianchetto, Uhlmann/Szabo, 9.e4",
  "E63": "King's Indian: Fianchetto, Panno, 8.Re1",
  "E64": "King's Indian: Fianchetto, Yugoslav, Early Exchange",
  "E65": "King's Indian: Fianchetto, Yugoslav, Exchange, 9.Bf4",
  "E66": "King's Indian: Fianchetto, Yugoslav Panno, Main Line, 12.Bb2 e5",
  "E67": "King's Indian: Fianchetto, Classical, 8.Qc2 c6",
  "E68": "King's Indian: Fianchetto, Classical, 8.e4 Re8",
  "E69": "King's Indian: Fianchetto, Classical, 9.h3 Re8 10.Re1 Qc7",
  "E70": "King's Indian: Kramer, 5...O-O 6.Ng3 e5 7.d5",
  "E71": "King's Indian: Makagonov, 5...O-O 6.Bg5 Nbd7",
  "E72": "King's Indian: Pomar System",
  "E73": "King's Indian: Averbakh, 6...Nbd7 7.Qd2 e5 8.d5 Nc5",
  "E74": "King's Indian: Averbakh, 6...c5 7.dxc5 Qa5 8.Bd2 Qxc5 9.Nf3 Bg4",
  "E75": "King's Indian: Averbakh, 7.d5 e6 8.Qd2 exd5 9.exd5 Re8 10.Nf3 Bg4",
  "E76": "King's Indian: Four Pawns Attack, Exchange",
  "E77": "King's Indian: Four Pawns Attack, 6.Be2 c5 7.d5 e6 8.Nf3 exd5 9.exd5",
  "E78": "King's Indian: Four Pawns Attack, 7.Nf3 cxd4",
  "E79": "King's Indian: Four Pawns Attack, Main Line, 9...Nxd4",
  "E80": "King's Indian: Saemisch, 5...Nc6",
  "E81": "King's Indian: Saemisch, 5...O-O 6.Nge2 e5",
  "E82": "King's Indian: Saemisch, Fianchetto, Bronstein Variation",
  "E83": "King's Indian: Saemisch, Ruban, 8.Qd2 Re8",
  "E84": "King's Indian: Saemisch, Panno Main Line, 9.Rb1",
  "E85": "King's Indian: Saemisch, Orthodox, Queenswap",
  "E86": "King's Indian: Saemisch, Orthodox, 7.Nge2 c6 8.Qd2 Nbd7 9.O-O-O a6 10.Kb1",
  "E87": "King's Indian: Saemisch, Orthodox, Bronstein, 9.g3",
  "E88": "King's Indian: Saemisch, Orthodox, Polugayevsky, 8...cxd5 9.cxd5 Nh5",
  "E89": "King's Indian: Saemisch, Orthodox Main Line, 9...Nbd7",
  "E90": "King's Indian: Zinnowitz, 6...h6",
  "E91": "King's Indian: Kazakh Variation, 7.O-O c6",
  "E92": "King's Indian: Petrosian, Stein, Main Line, 10...Qe8 11.O-O Nh7",
  "E93": "King's Indian: Petrosian, Main Line, 8.Qc2",
  "E94": "King's Indian: Glek, Main Line, 11.h3 h6",
  "E95": "King's Indian: 7.O-O Nbd7 8.Re1 Re8 9.Bf1",
  "E96": "King's Indian: 7.O-O Nbd7, Old Main Line, 10.Rb1 Re8 11.d5 Nc5 12.b3",
  "E97": "King's Indian: Mar del Plata, Odessa Variation",
  "E98": "King's Indian: Mar del Plata, Fischer Variation",
  "E99": "King's Indian: Mar del Plata, Benko Attack, 11...Nf6 12.Nd3"
};

async function fetchGameAPI(username, statsID) {
  try {
    console.log("Fetching games for user:", username); // Debug 1
    const params = new URLSearchParams({
      max: 300,
      perfType: "blitz",
      opening: true,
      clocks: true,
      evals: false,
      pgnInJson: true,
    });

    const baseURL = "https://lichess.org/api/games/user/";
    const GAMEURL = `${baseURL}${username}?${params.toString()}`;
    const response = await fetch(GAMEURL, {
      headers: {
        Accept: "application/x-ndjson",
      },
    });
    if (response.status !== 200) {
      throw new Error(`Failed to fetch games data: ${response.status}`);
    }

    const tableBody = document.getElementById(`${statsID}-table-body`);
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    // Initialize overall stats
    let winCount = 0,
      lossCount = 0,
      drawCount = 0,
      blitzGameCount = 0,
      totalGamesChecked = 0;

    // Initialize color-specific stats
    let whiteWinCount = 0,
      whiteLossCount = 0,
      whiteDrawCount = 0,
      whiteGameCount = 0;
    let blackWinCount = 0,
      blackLossCount = 0,
      blackDrawCount = 0,
      blackGameCount = 0;

    // Initialize ECO and game-end stats
    const ECOCounts = {};
    const ECOWins = {};
    const gameEndCounts = {
      mateWin: 0,
      resignWin: 0,
      timeWin: 0,
      mateLoss: 0,
      resignLoss: 0,
      timeLoss: 0,
    };
    let gameDurations = [];

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const lines = decoder.decode(value).split("\n").filter(Boolean);

      for (const line of lines) {
        const gameData = JSON.parse(line);
        totalGamesChecked++;

        // Overall stats
        if (gameData.speed === "blitz") {
          blitzGameCount++;
          if (gameData.winner) {
            if (
              (gameData.players.white.user?.name.toLowerCase() === username.toLowerCase() &&
                gameData.winner === "white") ||
              (gameData.players.black.user?.name.toLowerCase() === username.toLowerCase() &&
                gameData.winner === "black")
            ) {
              winCount++;
            } else {
              lossCount++;
            }
          } else {
            drawCount++;
          }
        }

        // White-specific stats
        if (gameData?.players?.white?.user?.name.toLowerCase() === username.toLowerCase()) {
          whiteGameCount++;
          if (gameData.winner === "white") {
            whiteWinCount++;
          } else if (gameData.winner === "black") {
            whiteLossCount++;
          } else {
            whiteDrawCount++;
          }
        }

        // Black-specific stats
        if (gameData?.players?.black?.user?.name.toLowerCase() === username.toLowerCase()) {
          blackGameCount++;
          if (gameData.winner === "black") {
            blackWinCount++;
          } else if (gameData.winner === "white") {
            blackLossCount++;
          } else {
            blackDrawCount++;
          }
        }

        // ECO statistics
        const eco = gameData.opening?.eco || "nonStandard";
        ECOCounts[eco] = (ECOCounts[eco] || 0) + 1;

        if (gameData.winner) {
          const isWhiteWinner = gameData.winner === "white" && 
                                gameData.players.white.user?.name.toLowerCase() === username.toLowerCase();
          const isBlackWinner = gameData.winner === "black" && 
                                gameData.players.black.user?.name.toLowerCase() === username.toLowerCase();

          if (isWhiteWinner || isBlackWinner) {
            ECOWins[eco] = (ECOWins[eco] || 0) + 1;
          }
        }

        // Game-end statistics
        const isUserWinner = (gameData.winner === "white" && 
                              gameData.players.white.user?.name.toLowerCase() === username.toLowerCase()) || 
                             (gameData.winner === "black" && 
                              gameData.players.black.user?.name.toLowerCase() === username.toLowerCase());
        const isUserLoser = !isUserWinner && gameData.winner;

        if (isUserWinner) {
          if (gameData.status === "mate") gameEndCounts.mateWin++;
          if (gameData.status === "resign") gameEndCounts.resignWin++;
          if (gameData.status === "outoftime") gameEndCounts.timeWin++;
        } else if (isUserLoser) {
          if (gameData.status === "mate") gameEndCounts.mateLoss++;
          if (gameData.status === "resign") gameEndCounts.resignLoss++;
          if (gameData.status === "outoftime") gameEndCounts.timeLoss++;
        }

        // Game length
        const duration = (gameData.lastMoveAt - gameData.createdAt) / 1000; // in seconds
        if (!isNaN(duration)) gameDurations.push(duration);
      }

      if (blitzGameCount >= 100 || totalGamesChecked >= 300) break;
    }

    // Calculate rates
    const winRate = ((winCount / blitzGameCount) * 100).toFixed(2) || "0.00";
    const lossRate = ((lossCount / blitzGameCount) * 100).toFixed(2) || "0.00";
    const drawRate = ((drawCount / blitzGameCount) * 100).toFixed(2) || "0.00";

    const whiteWinRate = ((whiteWinCount / whiteGameCount) * 100).toFixed(2) || "0.00";
    const whiteLoseRate = ((whiteLossCount / whiteGameCount) * 100).toFixed(2) || "0.00";
    const whiteDrawRate = ((whiteDrawCount / whiteGameCount) * 100).toFixed(2) || "0.00";

    const blackWinRate = ((blackWinCount / blackGameCount) * 100).toFixed(2) || "0.00";
    const blackLoseRate = ((blackLossCount / blackGameCount) * 100).toFixed(2) || "0.00";
    const blackDrawRate = ((blackDrawCount / blackGameCount) * 100).toFixed(2) || "0.00";

    // ECO stats
    const sortedECOCounts = Object.entries(ECOCounts).sort((a, b) => b[1] - a[1]);
    const topECO = sortedECOCounts[0]?.[0] || "N/A";
    const secondECO = sortedECOCounts[1]?.[0] || "N/A";

    const sortedECOWinRates = Object.entries(ECOCounts)
      .map(([eco, count]) => [eco, (ECOWins[eco] || 0) / count])
      .sort((a, b) => b[1] - a[1]);
    const topWinRateECO = sortedECOWinRates[0]?.[0] || "N/A";
    const secondWinRateECO = sortedECOWinRates[1]?.[0] || "N/A";

    const topECOName = ecoMapping[topECO] || "Unknown Opening";
    const secondECOName = ecoMapping[secondECO] || "Unknown Opening";
    const topWinECOName = ecoMapping[topWinRateECO] || "Unknown Opening"
    const secondWinECOName = ecoMapping[secondWinRateECO] || "Unknown Opening";

    // Game-end rates
    const totalWins = gameEndCounts.mateWin + gameEndCounts.resignWin + gameEndCounts.timeWin;
    const totalLosses = gameEndCounts.mateLoss + gameEndCounts.resignLoss + gameEndCounts.timeLoss;

    const mateWinRate = ((gameEndCounts.mateWin / totalWins) * 100).toFixed(2) || "0.00";
    const resignWinRate = ((gameEndCounts.resignWin / totalWins) * 100).toFixed(2) || "0.00";
    const timeWinRate = ((gameEndCounts.timeWin / totalWins) * 100).toFixed(2) || "0.00";

    const mateLossRate = ((gameEndCounts.mateLoss / totalLosses) * 100).toFixed(2) || "0.00";
    const resignLossRate = ((gameEndCounts.resignLoss / totalLosses) * 100).toFixed(2) || "0.00";
    const timeLossRate = ((gameEndCounts.timeLoss / totalLosses) * 100).toFixed(2) || "0.00";

    // Average game length
    const avgGameLength = (gameDurations.reduce((a, b) => a + b, 0) / gameDurations.length).toFixed(2) || "N/A";

    // Add new rows to the table
    // Add rows for color-specific stats
    addTableRow(tableBody, "White Win Rate (%)", whiteWinRate);
    addTableRow(tableBody, "White Loss Rate (%)", whiteLoseRate);
    addTableRow(tableBody, "White Draw Rate (%)", whiteDrawRate);
    addTableRow(tableBody, "White Game Count", whiteGameCount);

    addTableRow(tableBody, "Black Win Rate (%)", blackWinRate);
    addTableRow(tableBody, "Black Loss Rate (%)", blackLoseRate);
    addTableRow(tableBody, "Black Draw Rate (%)", blackDrawRate);
    addTableRow(tableBody, "Black Game Count", blackGameCount);
    addTableRow(tableBody, "Top ECO (Opening Name)", `${topECOName} (${topECO})`);
    addTableRow(tableBody, "Second ECO (Opening Name)", `${secondECOName} (${secondECO})`);
    addTableRow(tableBody, "Top Win Rate ECO", `${topWinECOName} (${topWinRateECO})`);
    addTableRow(tableBody, "Second Win Rate ECO", `${secondWinECOName} (${secondWinRateECO})`);

    addTableRow(tableBody, "Mate Win Rate (%)", mateWinRate);
    addTableRow(tableBody, "Resign Win Rate (%)", resignWinRate);
    addTableRow(tableBody, "Time Win Rate (%)", timeWinRate);

    addTableRow(tableBody, "Mate Loss Rate (%)", mateLossRate);
    addTableRow(tableBody, "Resign Loss Rate (%)", resignLossRate);
    addTableRow(tableBody, "Time Loss Rate (%)", timeLossRate);

    addTableRow(tableBody, "Average Game Length (s)", avgGameLength);
  } catch (e) {
    console.error(e);
  }
}






function addTableRow(tableBody, category, rating) {
  const row = document.createElement("tr");

  const categoryCell = document.createElement("td");
  categoryCell.textContent = category;

  const ratingCell = document.createElement("td");
  ratingCell.textContent = rating;

  row.appendChild(categoryCell);
  row.appendChild(ratingCell);

  tableBody.appendChild(row);
}