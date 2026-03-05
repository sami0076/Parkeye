import SwiftUI

struct SignUpView: View {
    @Bindable var viewModel: AuthViewModel
    @State private var confirmPassword = ""
    @State private var validationError: String?

    var body: some View {
        VStack(spacing: 24) {
            Spacer()

            VStack(spacing: 16) {
                TextField("Email", text: $viewModel.email)
                    .textContentType(.emailAddress)
                    .keyboardType(.emailAddress)
                    .autocapitalization(.none)
                    .textFieldStyle(.roundedBorder)

                SecureField("Password", text: $viewModel.password)
                    .textContentType(.newPassword)
                    .textFieldStyle(.roundedBorder)

                SecureField("Confirm Password", text: $confirmPassword)
                    .textContentType(.newPassword)
                    .textFieldStyle(.roundedBorder)
            }

            if let error = validationError ?? viewModel.errorMessage {
                Text(error)
                    .foregroundStyle(.red)
                    .font(.footnote)
                    .multilineTextAlignment(.center)
            }

            Button {
                guard viewModel.password == confirmPassword else {
                    validationError = "Passwords do not match."
                    return
                }
                validationError = nil
                Task { await viewModel.signUp() }
            } label: {
                Group {
                    if viewModel.isLoading {
                        ProgressView()
                    } else {
                        Text("Create Account")
                    }
                }
                .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .disabled(viewModel.isLoading)

            Spacer()
        }
        .padding(.horizontal, 32)
        .navigationTitle("Create Account")
        .navigationBarTitleDisplayMode(.large)
        .alert("Check Your Email", isPresented: $viewModel.needsEmailConfirmation) {
            Button("OK", role: .cancel) { }
        } message: {
            Text("A confirmation link has been sent to \(viewModel.email). Please check your inbox and confirm your account before signing in.")
        }
    }
}
