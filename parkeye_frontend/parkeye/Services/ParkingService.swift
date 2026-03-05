import Foundation

actor ParkingService {
    private let apiClient: APIClient

    init(apiClient: APIClient) {
        self.apiClient = apiClient
    }

    func fetchLots() async throws -> [Lot] {
        try await apiClient.get(APIEndpoints.lots)
    }

    func fetchLotDetail(id: UUID) async throws -> Lot {
        try await apiClient.get(APIEndpoints.lot(id: id))
    }

    func fetchLotHistory(id: UUID) async throws -> [OccupancyHistory] {
        let response: LotHistoryResponse = try await apiClient.get(APIEndpoints.lotHistory(id: id))
        return response.history
    }

    func fetchPredictions(lotId: UUID) async throws -> [Prediction] {
        let response: PredictionResponse = try await apiClient.get(APIEndpoints.predictions(lotId: lotId))
        return [
            Prediction(
                id: UUID(),
                lotId: lotId,
                minutesAhead: 15,
                predictedOccupancyPct: response.t15.pct * 100,
                predictedColor: hexFromSemanticColor(response.t15.color)
            ),
            Prediction(
                id: UUID(),
                lotId: lotId,
                minutesAhead: 30,
                predictedOccupancyPct: response.t30.pct * 100,
                predictedColor: hexFromSemanticColor(response.t30.color)
            )
        ]
    }

    func fetchRecommendations(
        permit: String,
        destLat: Double,
        destLon: Double,
        arrivalTime: String,
        durationMin: Int? = nil
    ) async throws -> [Recommendation] {
        let response: RecommendationsResponse = try await apiClient.get(
            APIEndpoints.recommendations(
                permit: permit,
                destLat: destLat,
                destLon: destLon,
                arrivalTime: arrivalTime,
                durationMin: durationMin
            )
        )
        return response.recommendations
    }

    func submitFeedback(_ request: FeedbackRequest) async throws {
        try await apiClient.postVoid(APIEndpoints.feedback, body: request)
    }
}

// MARK: - Private Prediction Decoding

private struct PredictionTimeBucket: Decodable {
    let pct: Double
    let color: String
}

private struct PredictionResponse: Decodable {
    let t15: PredictionTimeBucket
    let t30: PredictionTimeBucket
}
