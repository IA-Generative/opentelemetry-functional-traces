// Thunderbird 60.9.1 compatible example (background or a JS module):
// Uses XMLHttpRequest for ESR 60 compatibility.
// Call sendFunctionalEvent({ userEmail, appId, message, attributes, apiKey })
(function() {
  function sendFunctionalEvent(opts) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://localhost:8080/ingest", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("X-API-Key", opts.apiKey);
    xhr.onreadystatechange = function() {
      if (xhr.readyState === 4) {
        // Consider adding logging rather than alerts in production
        // dump('[Telemetry] status=' + xhr.status + ' body=' + xhr.responseText + '\n');
      }
    };
    var body = {
      user_email: (opts.userEmail || "").toLowerCase(),
      app_id: opts.appId || "thunderbird-plugin",
      message: opts.message || "action utilisateur",
      attributes: opts.attributes || {}
    };
    xhr.send(JSON.stringify(body));
  }

  // Example usage:
  // sendFunctionalEvent({
  //   userEmail: "user@example.org",
  //   appId: "thunderbird-60-addon-demo",
  //   message: "ouverture message",
  //   attributes: { mailbox: "INBOX" },
  //   apiKey: "dev_key_1"
  // });

  // Expose globally if needed
  this.sendFunctionalEvent = sendFunctionalEvent;
}).call(this);
