import Foundation

struct OccupancyHistory: Decodable, Identifiable {
    let hourOfDay: Int
    let dayOfWeek: Int
    let occupancyPct: Double
    let color: String

    var id: Int { dayOfWeek * 100 + hourOfDay }

    /// Synthesizes a Date in the current week for chart rendering.
    var timestamp: Date {
        let cal = Calendar.current
        let startOfWeek = cal.dateInterval(of: .weekOfYear, for: Date())!.start
        let day = cal.date(byAdding: .day, value: dayOfWeek, to: startOfWeek)!
        return cal.date(bySettingHour: hourOfDay, minute: 0, second: 0, of: day)!
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        hourOfDay = try c.decode(Int.self, forKey: .hourOfDay)
        dayOfWeek = try c.decode(Int.self, forKey: .dayOfWeek)
        let pct = try c.decode(Double.self, forKey: .occupancyPct)
        occupancyPct = pct * 100
        color = hexFromSemanticColor(try c.decode(String.self, forKey: .color))
    }

    private enum CodingKeys: CodingKey {
        case hourOfDay, dayOfWeek, occupancyPct, color
    }
}

struct LotHistoryResponse: Decodable {
    let lotId: UUID
    let history: [OccupancyHistory]
}
