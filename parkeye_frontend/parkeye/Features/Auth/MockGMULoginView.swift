import SwiftUI

/// Fake GMU CAS login for demo purposes.
/// Signs in with hardcoded demo credentials (demo@gmu.edu / demo123456).
/// Prereq: seed this user in Supabase before using.
struct MockGMULoginView: View {
    @Bindable var viewModel: AuthViewModel
    @State private var netId = ""

    var body: some View {
        VStack(spacing: 24) {
            Spacer()

            VStack(spacing: 8) {
                Image(systemName: "building.columns.fill")
                    .font(.system(size: 48))
                    .foregroundStyle(.tint)
                Text("GMU Single Sign-On")
                    .font(.title2.bold())
                Text("Demo mode — uses hardcoded credentials")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            VStack(spacing: 16) {
                TextField("NetID", text: $netId)
                    .textContentType(.username)
                    .autocapitalization(.none)
                    .textFieldStyle(.roundedBorder)
            }

            if let error = viewModel.errorMessage {
                Text(error)
                    .foregroundStyle(.red)
                    .font(.footnote)
                    .multilineTextAlignment(.center)
            }

            Button {
                viewModel.email = "demo@gmu.edu"
                viewModel.password = "demo123456"
                Task { await viewModel.signIn() }
            } label: {
                Group {
                    if viewModel.isLoading {
                        ProgressView()
                    } else {
                        Text("Continue")
                    }
                }
                .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .disabled(viewModel.isLoading)

            Spacer()
        }
        .padding(.horizontal, 32)
        .navigationTitle("GMU Login")
        .navigationBarTitleDisplayMode(.large)
    }
}
