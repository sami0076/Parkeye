import Foundation

actor WebSocketClient {
    private let url: URL
    private var task: URLSessionWebSocketTask?
    private var continuation: AsyncStream<[OccupancyUpdate]>.Continuation?

    private let decoder: JSONDecoder = {
        let d = JSONDecoder()
        d.keyDecodingStrategy = .convertFromSnakeCase
        return d
    }()

    init(url: URL) {
        self.url = url
    }

    func updates() -> AsyncStream<[OccupancyUpdate]> {
        AsyncStream { continuation in
            self.continuation = continuation
            Task { await self.connect() }
        }
    }

    private func connect() {
        task = URLSession.shared.webSocketTask(with: url)
        task?.resume()
        Task { await receiveLoop() }
    }

    private func receiveLoop() async {
        guard let task else { return }
        do {
            while true {
                let message = try await task.receive()
                let data: Data
                switch message {
                case .data(let d): data = d
                case .string(let s): data = Data(s.utf8)
                @unknown default: continue
                }
                if let updates = try? decoder.decode([OccupancyUpdate].self, from: data) {
                    continuation?.yield(updates)
                }
            }
        } catch {
            continuation?.yield([])
            try? await Task.sleep(for: .seconds(5))
            await reconnect()
        }
    }

    private func reconnect() async {
        task?.cancel(with: .goingAway, reason: nil)
        task = nil
        connect()
    }

    func disconnect() {
        task?.cancel(with: .goingAway, reason: nil)
        task = nil
        continuation?.finish()
        continuation = nil
    }
}
