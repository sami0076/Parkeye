import Foundation

@Observable
class LotDetailViewModel {
    var lot: Lot?
    var history: [OccupancyHistory] = []
    var predictions: [Prediction] = []
    var isLoading = false
    var errorMessage: String?

    private let lotId: UUID
    private let parkingService: ParkingService

    init(lotId: UUID, parkingService: ParkingService) {
        self.lotId = lotId
        self.parkingService = parkingService
    }

    func load() async {
        isLoading = true
        defer { isLoading = false }
        do {
            async let lotResult = parkingService.fetchLotDetail(id: lotId)
            async let historyResult = parkingService.fetchLotHistory(id: lotId)
            async let predictionsResult = parkingService.fetchPredictions(lotId: lotId)
            (lot, history, predictions) = try await (lotResult, historyResult, predictionsResult)
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
