import SwiftUI

struct HomeView: View {
    @Bindable var viewModel: HomeViewModel

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                VStack(spacing: 16) {
                    Picker("Permit Type", selection: $viewModel.selectedPermitType) {
                        ForEach(viewModel.permitTypes, id: \.self) { permit in
                            Text(permitLabel(permit)).tag(permit)
                        }
                    }
                    .pickerStyle(.segmented)
                    .onChange(of: viewModel.selectedPermitType) {
                        guard viewModel.hasSearched else { return }
                        Task { await viewModel.findParking() }
                    }

                    DatePicker("Arrival Time", selection: $viewModel.arrivalTime, displayedComponents: [.date, .hourAndMinute])
                        .labelsHidden()
                    .onChange(of: viewModel.arrivalTime) {
                        guard viewModel.hasSearched else { return }
                        Task { await viewModel.findParking() }
                    }

                    Button {
                        Task { await viewModel.findParking() }
                    } label: {
                        Group {
                            if viewModel.isLoading {
                                ProgressView()
                            } else {
                                Text("Find Parking")
                            }
                        }
                        .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(viewModel.isLoading)
                }
                .padding()

                Divider()

                if let error = viewModel.errorMessage {
                    ContentUnavailableView("Error", systemImage: "exclamationmark.triangle",
                                          description: Text(error))
                } else if viewModel.hasSearched && viewModel.recommendations.isEmpty {
                    ContentUnavailableView("No Results", systemImage: "car.fill",
                                          description: Text("No lots available for this permit type."))
                } else if !viewModel.recommendations.isEmpty {
                    List(viewModel.recommendations) { rec in
                        RecommendationRow(recommendation: rec)
                    }
                    .listStyle(.plain)
                } else {
                    Spacer()
                    Text("Select a permit type and tap Find Parking")
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                        .padding()
                    Spacer()
                }
            }
            .navigationTitle("Find Parking")
        }
    }
}

private func permitLabel(_ raw: String) -> String {
    switch raw {
    case "general":     return "General"
    case "west_campus": return "West Campus"
    case "faculty":     return "Faculty"
    default:            return raw.capitalized
    }
}

private struct RecommendationRow: View {
    let recommendation: Recommendation

    var body: some View {
        HStack(spacing: 12) {
            Circle()
                .fill(Color(hex: recommendation.color))
                .frame(width: 14, height: 14)

            VStack(alignment: .leading, spacing: 2) {
                Text(recommendation.lotName)
                    .font(.body)
                if let permits = recommendation.permitTypes, !permits.isEmpty {
                    Text(permits.joined(separator: ", "))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                if let walk = recommendation.walkMinutes {
                    Text("\(Int(walk)) min walk")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            Spacer()

            Text("\(Int(recommendation.occupancyPct))%")
                .font(.callout.monospacedDigit())
                .foregroundStyle(.secondary)
        }
        .padding(.vertical, 4)
    }
}
