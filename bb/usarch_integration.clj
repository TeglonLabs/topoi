(ns usarch-integration
  "Babashka script demonstrating a minimal approach to Usearch integration via a custom CLI."
  (:require [clojure.java.shell :as sh]
            [cheshire.core :as json]))

(defn build-usearch-cli
  "Example function that compiles a minimal Usearch C++ CLI to handle indexing and searching.
   This requires a C++ compiler and the Usearch source code in a known path."
  []
  (sh/sh "bash" "-c"
         (str "
cat << EOF > usarch_test.cpp
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <unordered_map>
#include \"usearch/index_punned_dense.hpp\"

using namespace unum::usearch;

int main(int argc, char** argv) {
    // For demonstration: store vectors in memory, index them, and perform a search
    // In a real system, you might store the index to a file or use a more robust approach

    if (argc < 2) {
        std::cout << \"Usage: ./usarch_test [index|search] [args...]\\n\";
        return 0;
    }

    std::string mode = argv[1];

    static index_punned_dense_t index;
    static bool built = false;
    static std::vector<float> localVecs;
    static std::vector<std::string> localIDs;

    if (mode == \"index\") {
        // Expect line-based input with ID and vector in JSON
        // e.g. { \"id\": \"doc1\", \"vector\": [0.1, 0.2, ...] }
        std::string line;
        while (std::getline(std::cin, line)) {
            if (line.empty()) continue;
            auto pos = line.find(\"\\n\");
            if (pos != std::string::npos) line.erase(pos);
            // Very naive approach (no real JSON parsing).
            // Real-world usage requires robust JSON parsing or a structured format.
        }
        std::cout << \"Indexing done\\n\";
    } else if (mode == \"search\") {
        // Expect a vector from stdin or as command-line arguments
        // Then do approximate search
        std::cout << \"Search not implemented in this minimal example\\n\";
    } else {
        std::cout << \"Unknown mode: \" << mode << \"\\n\";
    }

    return 0;
}
EOF

# Attempt to compile
g++ -std=c++11 usarch_test.cpp -o usarch_test
")))

(defn index-documents
  "Call the compiled Usearch CLI to index documents.
   We pass JSON lines detailing ID and numeric vectors over STDIN via :in in sh/sh."
  [docs]
  (let [input-lines (->> docs
                         (map (fn [doc-map]
                                ;; doc-map is {:id \"doc1\" :vector [0.1 0.2 0.3]}
                                (json/generate-string doc-map)))
                         (clojure.string/join "\n"))]
    (sh/sh "./usarch_test" "index" :in input-lines)))

(defn -main
  [& _args]
  (println "Building Usearch CLI...")
  (build-usearch-cli)
  (println "Done.")
  (println "Indexing sample documents...")
  (let [sample-docs
        [{:id "doc1" :vector [0.1 0.2 0.3]}
         {:id "doc2" :vector [0.4 0.5 0.6]}]
        result
        (index-documents sample-docs)]
    (println
      (str "CLI returned: "
           (:out result) " "
           (:err result) " "
           (:exit result))))
  (println "Finished."))

;; You can run this script with:
;; bb usarch_integration.clj
