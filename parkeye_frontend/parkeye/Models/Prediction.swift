import Foundation

struct Prediction: Identifiable {
    let id: UUID
    let lotId: UUID
    let minutesAhead: Int
    let predictedOccupancyPct: Double
    let predictedColor: String
}
