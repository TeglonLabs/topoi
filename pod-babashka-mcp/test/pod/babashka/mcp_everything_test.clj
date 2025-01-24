(ns pod.babashka.mcp-everything-test
  (:require [clojure.test :refer [deftest testing is use-fixtures]]
            [pod.babashka.mcp :as mcp]
            [clojure.core.async :refer [<!! timeout chan >! close!]]
            [babashka.process :refer [process]]
            [clojure.java.io :as io]))

(def mock-server-process (atom nil))

(defn start-mock-server []
  (reset! mock-server-process
          (process ["bb" "test/mock_everything_server.clj"]
                  {:inherit true
                   :shutdown #(when % (.destroy %))})))

(defn stop-mock-server []
  (when-let [proc @mock-server-process]
    (.destroy proc)
    (reset! mock-server-process nil)))

(use-fixtures :each
  (fn [test-fn]
    (start-mock-server)
    (Thread/sleep 1000) ; Give server time to start
    (test-fn)
    (stop-mock-server)))

(deftest test-sync-operations
  (testing "Synchronous tool execution"
    (mcp/with-session [session {:command "bb"
                               :args ["test/mock_everything_server.clj"]}]
      (let [result (mcp/call-tool session "sync_tool" {:arg "test"})]
        (is (= "Processed: test"
               (-> result :content first :text)))))))

(deftest test-async-operations
  (testing "Asynchronous tool execution"
    (mcp/with-session [session {:command "bb"
                               :args ["test/mock_everything_server.clj"]}]
      (let [result (<!! (mcp/call-tool-async session "async_tool" {:delay 1}))]
        (is (= "Async operation complete"
               (-> result :content first :text)))))))

(deftest test-streaming-operations
  (testing "Streaming tool output"
    (mcp/with-session [session {:command "bb"
                               :args ["test/mock_everything_server.clj"]}]
      (let [results (atom [])
            ch (chan)]
        (mcp/call-tool session "streaming_tool" 
                      {:count 3}
                      #(do (swap! results conj %)
                          (when (= "Stream complete" 
                                 (-> % :content first :text))
                            (>! ch :done))))
        (<!! (timeout 5000))
        (is (= 4 (count @results))) ; 3 items + completion
        (is (= "Stream complete"
               (-> @results last :content first :text)))))))

(deftest test-error-handling
  (testing "Error handling in tools"
    (mcp/with-session [session {:command "bb"
                               :args ["test/mock_everything_server.clj"]}]
      (testing "Validation error"
        (is (thrown-with-msg? Exception #"Validation error"
              (mcp/call-tool session "error_tool" 
                            {:error_type "validation"}))))
      
      (testing "Runtime error"
        (is (thrown-with-msg? Exception #"Runtime error"
              (mcp/call-tool session "error_tool"
                            {:error_type "runtime"}))))
      
      (testing "Timeout handling"
        (is (thrown-with-msg? Exception #"Timeout"
              (mcp/call-tool session "error_tool"
                            {:error_type "timeout"}
                            {:timeout 1000})))))))

(deftest test-resource-handling
  (testing "Resource operations"
    (mcp/with-session [session {:command "bb"
                               :args ["test/mock_everything_server.clj"]}]
      (testing "Static resource"
        (let [result (mcp/read-resource session "mock://static/data")]
          (is (= "Static content"
                 (-> result :contents first :text)))))
      
      (testing "Dynamic resource"
        (let [result (mcp/read-resource session "mock://dynamic/test")]
          (is (= "test"
                 (-> result :contents first :text :param)))))
      
      (testing "Streaming resource"
        (let [events (atom [])]
          (mcp/subscribe session "mock://stream/events"
                        #(swap! events conj %))
          (<!! (timeout 5500))
          (is (= 5 (count @events))))))))

(deftest test-capabilities
  (testing "Server capabilities"
    (mcp/with-session [session {:command "bb"
                               :args ["test/mock_everything_server.clj"]}]
      (testing "Tool listing"
        (let [tools (mcp/list-tools session)]
          (is (= #{"sync_tool" "async_tool" 
                  "streaming_tool" "error_tool"}
                 (set (map :name tools))))))
      
      (testing "Resource listing"
        (let [resources (mcp/list-resources session)]
          (is (= #{"mock://static/data"
                  "mock://dynamic/{param}"
                  "mock://stream/events"}
                 (set (map :uri resources)))))))))

(deftest test-configuration
  (testing "Configuration handling"
    (let [config {:command "bb"
                  :args ["test/mock_everything_server.clj"]
                  :env {"DEBUG" "true"}
                  :timeout 5000}]
      (mcp/with-session [session config]
        (testing "Connection establishment"
          (is (map? session))
          (is (contains? session :pod/id)))
        
        (testing "Environment variables"
          (is (= "true"
                 (System/getenv "DEBUG"))))
        
        (testing "Timeout configuration"
          (is (thrown? Exception
                (mcp/call-tool session "error_tool"
                              {:error_type "timeout"}))))))))
