import unittest
from unittest.mock import patch, MagicMock
import io
import json

from scripts.hermes_agent_bridge import make_request

class TestHermesAgentBridge(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_make_request_get_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"status": "online", "authenticated": True}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = make_request("/api/hermes/status")
        self.assertEqual(res["status"], "online")
        self.assertTrue(res["authenticated"])

    @patch("urllib.request.urlopen")
    def test_make_request_post_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"success": True, "action": "draft_post"}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = make_request("/api/hermes/dispatch", method="POST", data={"action": "draft_post"})
        self.assertTrue(res["success"])
        self.assertEqual(res["action"], "draft_post")

if __name__ == "__main__":
    unittest.main()
