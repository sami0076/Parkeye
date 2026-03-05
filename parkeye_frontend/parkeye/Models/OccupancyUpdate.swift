import Foundation

struct OccupancyUpdate: Decodable {
    let lotId: UUID
    let occupancyPct: Double
    let color: String

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        lotId = try c.decode(UUID.self, forKey: .lotId)
        let pct = try c.decode(Double.self, forKey: .occupancyPct)
        occupancyPct = pct * 100
        color = hexFromSemanticColor(try c.decode(String.self, forKey: .color))
    }

    private enum CodingKeys: CodingKey {
        case lotId, occupancyPct, color
    }
}
