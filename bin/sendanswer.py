from __future__ import absolute_import
import json
import os
import re
import sys
from random import choice

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../lib"))
# pylint: disable=wrong-import-position
from splunklib import client
from splunklib.binding import HTTPError
from splunklib.results import JSONResultsReader
from splunklib.searchcommands import (
    dispatch,
    Configuration,
    ReportingCommand,
)

@Configuration()
class SendAnswerCommand(ReportingCommand):
    @Configuration()
    def map(self, records):
        """map passes all incoming records back out. This command has no real "map" functionality"""
        for record in records:
            yield record

    def reduce(self, records):
        """reduce validates the results passed to it, and sends a respose event to the answers index"""
        answer_record = {}

        for record_count, record in enumerate(records):
            if record_count > 0:
                self.error_exit(None, "Unable to create answer event. More than one result passed to sendanswer")

            if "answer" not in record:
                self.error_exit(None, 'Unable to create answer event. Record passed to sendanswer missing "answer" field')

            try:
                response = self.service.get("/services/authentication/current-context", output_mode="json")
            except HTTPError as exc:
                self.error_exit(exc, f"Unable to create answer event. Error getting current-context")

            results = json.load(response["body"])
            entries = results["entry"]
            for entry_count, entry in enumerate(entries):
                if entry_count > 0:
                    self.error_exit(None, "Unable to create answer event. More than one entry returned for current-context")

                duration_ms = 0
                # only top-level commands are counted
                # sub-command durations are already accounted by their top-level command
                duration_pattern = re.compile("^duration\.command\.[^.]+$")

                for key, value in dict(self.search_results_info.countMap).items():
                    if duration_pattern.search(key):
                        duration_ms += int(value)

                # need to set owner="nobody" to use kvstore
                service = client.connect(owner="nobody", token=self.service.token, user="-", app="spling_bee")
                table = service.kvstore["spling_bee_start"]
                current_results = table.data.query(current=1)

                current_category = None
                current_question = None
                for current_count, current_result in enumerate(current_results):
                    if current_count > 0:
                        self.error_exit(None, "Unable to create answer event. More than one spling_bee_start entry with current=1.")

                    current_category = current_result["category"]
                    current_question = current_result["question"]

                if not (current_category and current_category):
                    self.error_exit(None, "Unable to create answer event. No current category/question.")

                answer_record = {
                    "answer": record["answer"],
                    "username": entry["content"]["username"],
                    "realname": entry["content"]["realname"],
                    "search": self.search_results_info.search,
                    "duration_ms": duration_ms,
                    "category": current_category,
                    "question": current_question,
                }

        if not answer_record:
            self.error_exit(None, "Unable to create answer event. Did you pass in a result?")

        try:
            self.service.post("/services/receivers/simple", index="spl_bee", sourcetype="response", body=json.dumps(answer_record))
        except HTTPError as exc:
            self.error_exit(exc, f"Unable to create answer event. Event creation failed: {exc}")
        yield answer_record

if __name__ == "__main__":
    dispatch(SendAnswerCommand, sys.argv, sys.stdin, sys.stdout, __name__)
