import SwiftUI

struct FeedbackView: View {
    @Bindable var viewModel: FeedbackViewModel
    var lots: [Lot]

    var body: some View {
        NavigationStack {
            if viewModel.isSubmitted {
                SuccessView {
                    viewModel.reset()
                }
            } else {
                Form {
                    Section("Lot") {
                        Picker("Select Lot", selection: $viewModel.selectedLotId) {
                            Text("None").tag(UUID?.none)
                            ForEach(lots) { lot in
                                Text(lot.name).tag(Optional(lot.id))
                            }
                        }
                    }

                    Section("Accuracy Rating") {
                        StarRatingView(rating: $viewModel.accuracyRating)
                    }

                    Section("Experience Rating") {
                        StarRatingView(rating: $viewModel.experienceRating)
                    }

                    Section("Note (optional)") {
                        TextField("Your experience...", text: $viewModel.note, axis: .vertical)
                            .lineLimit(3...6)
                    }

                    if let error = viewModel.errorMessage {
                        Section {
                            Text(error)
                                .foregroundStyle(.red)
                                .font(.footnote)
                        }
                    }

                    Section {
                        Button {
                            Task { await viewModel.submit() }
                        } label: {
                            Group {
                                if viewModel.isLoading {
                                    ProgressView()
                                } else {
                                    Text("Submit Feedback")
                                }
                            }
                            .frame(maxWidth: .infinity)
                        }
                        .disabled(
                            viewModel.isLoading ||
                            viewModel.accuracyRating == 0 ||
                            viewModel.experienceRating == 0 ||
                            viewModel.selectedLotId == nil
                        )
                    }
                }
                .navigationTitle("Feedback")
            }
        }
    }
}

// MARK: - Subviews

private struct StarRatingView: View {
    @Binding var rating: Int

    var body: some View {
        HStack(spacing: 8) {
            ForEach(1...5, id: \.self) { star in
                Image(systemName: star <= rating ? "star.fill" : "star")
                    .font(.title2)
                    .foregroundStyle(star <= rating ? .yellow : .secondary)
                    .onTapGesture { rating = star }
            }
        }
        .padding(.vertical, 4)
    }
}

private struct SuccessView: View {
    var onReset: () -> Void

    var body: some View {
        VStack(spacing: 24) {
            Spacer()
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 64))
                .foregroundStyle(.green)
            Text("Thank you!")
                .font(.title2.bold())
            Text("Your feedback has been submitted.")
                .foregroundStyle(.secondary)
            Button("Submit Another") { onReset() }
                .buttonStyle(.bordered)
            Spacer()
        }
        .navigationTitle("Feedback")
    }
}
