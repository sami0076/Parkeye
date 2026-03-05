import Foundation

@Observable
class MapViewModel {
    var lots: [Lot] = []
    var isLoading = false
    var errorMessage: String?
    var selectedLot: Lot?

    private let parkingService: ParkingService
    private let webSocketClient: WebSocketClient

    init(parkingService: ParkingService, webSocketClient: WebSocketClient) {
        self.parkingService = parkingService
        self.webSocketClient = webSocketClient
    }

    func loadLots() async {
        isLoading = true
        defer { isLoading = false }
        do {
            lots = try await parkingService.fetchLots()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func connectLiveOccupancy() async {
        let stream = await webSocketClient.updates()
        var receivedAny = false
        for await updates in stream {
            receivedAny = true
            applyUpdates(updates)
        }
        // Stream ended — fall back to polling
        if receivedAny {
            await pollFallback()
        }
    }

    private func applyUpdates(_ updates: [OccupancyUpdate]) {
        var map: [UUID: OccupancyUpdate] = [:]
        for u in updates { map[u.lotId] = u }
        lots = lots.map { lot in
            guard let u = map[lot.id] else { return lot }
            var updated = lot
            updated.occupancyPct = u.occupancyPct
            updated.color = u.color
            return updated
        }
    }

    private func pollFallback() async {
        while !Task.isCancelled {
            try? await Task.sleep(for: .seconds(30))
            await loadLots()
        }
    }

    func selectLot(id: UUID) {
        selectedLot = lots.first { $0.id == id }
    }

    func clearSelection() {
        selectedLot = nil
    }
}
