## GitHub Copilot Chat

- Extension: 0.45.1 (prod)
- VS Code: 1.117.0 (10c8e557c8b9f9ed0a87f61f1c9a44bde731c409)
- OS: win32 10.0.26200 x64
- GitHub Account: AprilV

## Network

User Settings:
```json
  "http.systemCertificatesNode": true,
  "github.copilot.advanced.debug.useElectronFetcher": true,
  "github.copilot.advanced.debug.useNodeFetcher": false,
  "github.copilot.advanced.debug.useNodeFetchFetcher": true
```

Connecting to https://api.github.com:
- DNS ipv4 Lookup: Error (23 ms): getaddrinfo ENOTFOUND api.github.com
- DNS ipv6 Lookup: Error (0 ms): getaddrinfo ENOTFOUND api.github.com
- Proxy URL: None (1 ms)
- Electron fetch (configured): Error (1 ms): Error: net::ERR_INTERNET_DISCONNECTED
	at SimpleURLLoaderWrapper.<anonymous> (node:electron/js2c/utility_init:2:10684)
	at SimpleURLLoaderWrapper.emit (node:events:519:28)
  {"is_request_error":true,"network_process_crashed":false}
- Node.js https: Error (10 ms): Error: getaddrinfo ENOTFOUND api.github.com
	at GetAddrInfoReqWrap.onlookupall [as oncomplete] (node:dns:122:26)
- Node.js fetch: Error (16 ms): TypeError: fetch failed
	at node:internal/deps/undici/undici:14902:13
	at process.processTicksAndRejections (node:internal/process/task_queues:103:5)
	at async t._fetch (c:\Users\april\.vscode\extensions\github.copilot-chat-0.45.1\dist\extension.js:5307:5229)
	at async t.fetch (c:\Users\april\.vscode\extensions\github.copilot-chat-0.45.1\dist\extension.js:5307:4541)
	at async u (c:\Users\april\.vscode\extensions\github.copilot-chat-0.45.1\dist\extension.js:5339:186)
	at async Eg._executeContributedCommand (file:///c:/Users/april/AppData/Local/Programs/Microsoft%20VS%20Code/10c8e557c8/resources/app/out/vs/workbench/api/node/extensionHostProcess.js:501:48675)
  Error: getaddrinfo ENOTFOUND api.github.com
  	at GetAddrInfoReqWrap.onlookupall [as oncomplete] (node:dns:122:26)

Connecting to https://api.githubcopilot.com/_ping:
- DNS ipv4 Lookup: Error (0 ms): getaddrinfo ENOTFOUND api.githubcopilot.com
- DNS ipv6 Lookup: Error (1 ms): getaddrinfo ENOTFOUND api.githubcopilot.com
- Proxy URL: None (2179 ms)
- Electron fetch (configured): Error (1183 ms): Error: net::ERR_INTERNET_DISCONNECTED
	at SimpleURLLoaderWrapper.<anonymous> (node:electron/js2c/utility_init:2:10684)
	at SimpleURLLoaderWrapper.emit (node:events:519:28)
  {"is_request_error":true,"network_process_crashed":false}
- Node.js https: HTTP 200 (339 ms)
- Node.js fetch: HTTP 200 (301 ms)

Connecting to https://copilot-proxy.githubusercontent.com/_ping:
- DNS ipv4 Lookup: 138.91.182.224 (38 ms)
- DNS ipv6 Lookup: Error (28 ms): getaddrinfo ENOTFOUND copilot-proxy.githubusercontent.com
- Proxy URL: None (1 ms)
- Electron fetch (configured): HTTP 200 (215 ms)
- Node.js https: HTTP 200 (349 ms)
- Node.js fetch: HTTP 200 (164 ms)

Connecting to https://mobile.events.data.microsoft.com: Error (491 ms): Error: net::ERR_NETWORK_CHANGED
	at SimpleURLLoaderWrapper.<anonymous> (node:electron/js2c/utility_init:2:10684)
	at SimpleURLLoaderWrapper.emit (node:events:519:28)
  {"is_request_error":true,"network_process_crashed":false}
Connecting to https://dc.services.visualstudio.com: HTTP 404 (2081 ms)
Connecting to https://copilot-telemetry.githubusercontent.com/_ping: HTTP 200 (279 ms)
Connecting to https://telemetry.individual.githubcopilot.com/_ping: HTTP 200 (303 ms)
Connecting to https://default.exp-tas.com: HTTP 400 (138 ms)

Number of system certificates: 170

## Documentation

In corporate networks: [Troubleshooting firewall settings for GitHub Copilot](https://docs.github.com/en/copilot/troubleshooting-github-copilot/troubleshooting-firewall-settings-for-github-copilot).