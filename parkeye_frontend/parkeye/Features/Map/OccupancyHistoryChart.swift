import SwiftUI
import Charts

struct OccupancyHistoryChart: View {
    let history: [OccupancyHistory]

    var body: some View {
        Chart(history) { point in
            LineMark(
                x: .value("Time", point.timestamp),
                y: .value("Occupancy", point.occupancyPct)
            )
            .interpolationMethod(.catmullRom)
            .foregroundStyle(Color.accentColor)

            AreaMark(
                x: .value("Time", point.timestamp),
                y: .value("Occupancy", point.occupancyPct)
            )
            .interpolationMethod(.catmullRom)
            .foregroundStyle(Color.accentColor.opacity(0.15))
        }
        .chartYScale(domain: 0...100)
        .chartYAxis {
            AxisMarks(values: [0, 25, 50, 75, 100]) { value in
                AxisGridLine()
                AxisValueLabel { Text("\(value.as(Int.self) ?? 0)%") }
            }
        }
        .frame(height: 160)
    }
}
