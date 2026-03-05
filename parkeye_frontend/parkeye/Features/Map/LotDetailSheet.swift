import SwiftUI

struct LotDetailSheet: View {
    @State private var viewModel: LotDetailViewModel

    init(lotId: UUID, parkingService: ParkingService) {
        _viewModel = State(initialValue: LotDetailViewModel(lotId: lotId, parkingService: parkingService))
    }

    var body: some View {
        NavigationStack {
            Group {
                if viewModel.isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if let error = viewModel.errorMessage {
                    ContentUnavailableView("Error", systemImage: "exclamationmark.triangle",
                                          description: Text(error))
                } else if let lot = viewModel.lot {
                    ScrollView {
                        VStack(alignment: .leading, spacing: 20) {
                            OccupancyIndicator(lot: lot)

                            if !viewModel.predictions.isEmpty {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Predictions")
                                        .font(.headline)
                                    HStack {
                                        ForEach(viewModel.predictions) { prediction in
                                            PredictionChip(prediction: prediction)
                                        }
                                    }
                                }
                            }

                            if !viewModel.history.isEmpty {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Weekly Pattern")
                                        .font(.headline)
                                    OccupancyHistoryChart(history: viewModel.history)
                                }
                            }

                            if let permits = lot.permitTypes, !permits.isEmpty {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text("Permit Types")
                                        .font(.headline)
                                    Text(permits.joined(separator: ", "))
                                        .foregroundStyle(.secondary)
                                }
                            }
                        }
                        .padding()
                    }
                }
            }
            .navigationTitle(viewModel.lot?.name ?? "Lot Details")
            .navigationBarTitleDisplayMode(.large)
        }
        .presentationDetents([.medium, .large])
        .task { await viewModel.load() }
    }
}

// MARK: - Subviews

private struct OccupancyIndicator: View {
    let lot: Lot

    var body: some View {
        HStack(spacing: 16) {
            Circle()
                .fill(Color(hex: lot.color))
                .frame(width: 20, height: 20)

            VStack(alignment: .leading, spacing: 2) {
                Text("\(Int(lot.occupancyPct))% full")
                    .font(.title2.bold())
                Text("Capacity: \(lot.capacity) spaces")
                    .foregroundStyle(.secondary)
            }
        }
        .padding()
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12))
    }
}

private struct PredictionChip: View {
    let prediction: Prediction

    var body: some View {
        VStack(spacing: 4) {
            Text("+\(prediction.minutesAhead)m")
                .font(.caption2)
                .foregroundStyle(.secondary)
            Text("\(Int(prediction.predictedOccupancyPct))%")
                .font(.callout.bold())
            Circle()
                .fill(Color(hex: prediction.predictedColor))
                .frame(width: 10, height: 10)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 10))
    }
}
