import SwiftUI

struct ProfileView: View {
    @Bindable var viewModel: ProfileViewModel
    var authViewModel: AuthViewModel

    var body: some View {
        NavigationStack {
            List {
                Section("Account") {
                    if viewModel.userEmail.isEmpty {
                        Text("Loading...")
                            .foregroundStyle(.secondary)
                    } else {
                        LabeledContent("Email", value: viewModel.userEmail)
                    }
                }

                Section("App") {
                    LabeledContent("Version", value: appVersion)
                }

                Section {
                    Button(role: .destructive) {
                        Task { await viewModel.signOut(authViewModel: authViewModel) }
                    } label: {
                        Text("Sign Out")
                            .frame(maxWidth: .infinity, alignment: .center)
                    }
                }
            }
            .navigationTitle("Profile")
            .task { await viewModel.loadUser() }
        }
    }

    private var appVersion: String {
        Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "—"
    }
}
