// Run after tests/check.py on macOS: swift tests/check-wkwebview.swift
import AppKit
import WebKit

@MainActor final class DocumentCheck: NSObject, WKNavigationDelegate {
    let view = WKWebView(frame: NSRect(x: 0, y: 0, width: 1000, height: 1200))
    let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 1000, height: 1200),
                          styleMask: [], backing: .buffered, defer: false)
    let tests = URL(fileURLWithPath: #filePath).deletingLastPathComponent()

    func start() {
        window.contentView = view
        view.navigationDelegate = self
        let output = tests.appendingPathComponent("output/document-adapters.html")
        view.loadFileURL(output, allowingReadAccessTo: output.deletingLastPathComponent())
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        Task { @MainActor in
            do {
                let script = try String(contentsOf: tests.appendingPathComponent("document-browser.js"), encoding: .utf8)
                let result = try await view.callAsyncJavaScript(
                    "await document.fonts.ready; return (\(script));",
                    arguments: [:], in: nil, contentWorld: .page)
                guard let count = (result as? [String: Any])?["passed"] as? Int else {
                    throw NSError(domain: "letmeout", code: 1,
                                  userInfo: [NSLocalizedDescriptionKey: "Missing browser check results"])
                }
                print("PASS: \(count) WKWebView document layout checks")
                exit(0)
            } catch {
                print("FAIL: \(error)")
                exit(1)
            }
        }
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        print("FAIL: \(error)")
        exit(1)
    }
}

MainActor.assumeIsolated {
    let app = NSApplication.shared
    app.setActivationPolicy(.prohibited)
    let check = DocumentCheck()
    check.start()
    Timer.scheduledTimer(withTimeInterval: 30, repeats: false) { _ in
        print("FAIL: WKWebView verification timed out")
        exit(1)
    }
    withExtendedLifetime(check) { app.run() }
}
