(ns pod.babashka.mcp-test
  (:require [clojure.test :refer [deftest testing is]]
            [pod.babashka.mcp :as mcp]
            [babashka.pods :as pods]))

(defn with-test-server [f]
  (let [server-process (future
                        (pods/load-pod ["bb" "example_mcp_server.clj"]))]
    (try
      (f)
      (finally
        (future-cancel server-process)))))

(deftest connect-test
  (with-test-server
    (fn []
      (testing "connect with valid options"
        (let [session (mcp/connect {:command "bb"
                                  :args ["example_mcp_server.clj"]})]
          (is (map? session))
          (is (contains? session :pod/id))
          (mcp/disconnect session)))

      (testing "connect with invalid command"
        (is (thrown? Exception
                     (mcp/connect {:command "nonexistent"})))))))

(deftest tools-test
  (with-test-server
    (fn []
      (testing "list tools"
        (mcp/with-session [session {:command "bb"
                                   :args ["example_mcp_server.clj"]}]
          (let [tools (mcp/list-tools session)]
            (is (sequential? tools))
            (is (= "list_directory" (-> tools first :name))))))

      (testing "call tool"
        (mcp/with-session [session {:command "bb"
                                   :args ["example_mcp_server.clj"]}]
          (let [result (mcp/call-tool session "list_directory" {:path "."})]
            (is (map? result))
            (is (vector? (:content result)))))))))

(deftest resources-test
  (with-test-server
    (fn []
      (testing "list resources"
        (mcp/with-session [session {:command "bb"
                                   :args ["example_mcp_server.clj"]}]
          (let [resources (mcp/list-resources session)]
            (is (map? resources))
            (is (vector? (:resources resources)))))))))

(deftest async-test
  (with-test-server
    (fn []
      (testing "async tool call"
        (mcp/with-session [session {:command "bb"
                                   :args ["example_mcp_server.clj"]}]
          (let [p (mcp/call-tool-async session "list_directory" {:path "."})
                result (deref p 1000 :timeout)]
            (is (not= :timeout result))
            (is (map? result))
            (is (vector? (:content result)))))))))

(deftest subscription-test
  (with-test-server
    (fn []
      (testing "resource subscription"
        (mcp/with-session [session {:command "bb"
                                   :args ["example_mcp_server.clj"]}]
          (let [updates (atom [])
                _ (mcp/subscribe session "test://resource"
                               #(swap! updates conj %))
                ;; Wait a bit for potential updates
                _ (Thread/sleep 100)]
            (is (vector? @updates))))))))

(deftest error-handling-test
  (with-test-server
    (fn []
      (testing "invalid tool call"
        (mcp/with-session [session {:command "bb"
                                   :args ["example_mcp_server.clj"]}]
          (is (thrown? Exception
                       (mcp/call-tool session "nonexistent_tool" {})))))

      (testing "invalid resource read"
        (mcp/with-session [session {:command "bb"
                                   :args ["example_mcp_server.clj"]}]
          (is (thrown? Exception
                       (mcp/read-resource session "invalid://uri"))))))))
