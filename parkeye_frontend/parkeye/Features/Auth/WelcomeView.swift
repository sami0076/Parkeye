import SwiftUI

struct WelcomeView: View {
    var viewModel: AuthViewModel

    var body: some View {
        NavigationStack {
            VStack(spacing: 32) {
                Spacer()

                VStack(spacing: 8) {
                    Image(systemName: "parkingsign.circle.fill")
                        .font(.system(size: 72))
                        .foregroundStyle(.tint)

                    Text("ParkEye")
                        .font(.largeTitle.bold())

                    Text("GMU Parking")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }

                Spacer()

                VStack(spacing: 12) {
                    NavigationLink {
                        SignInView(viewModel: viewModel)
                    } label: {
                        Text("Sign In")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)

                    NavigationLink {
                        SignUpView(viewModel: viewModel)
                    } label: {
                        Text("Create Account")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)

                    NavigationLink {
                        MockGMULoginView(viewModel: viewModel)
                    } label: {
                        Label("Continue with GMU", systemImage: "building.columns")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                }
                .padding(.horizontal, 32)
                .padding(.bottom, 40)
            }
        }
    }
}
