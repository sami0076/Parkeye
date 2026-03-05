import SwiftUI
import CoreLocation

struct PermissionsView: View {
    var locationService: LocationService
    var onComplete: () -> Void

    var body: some View {
        VStack(spacing: 32) {
            Spacer()

            VStack(spacing: 12) {
                Image(systemName: "location.circle.fill")
                    .font(.system(size: 64))
                    .foregroundStyle(.tint)

                Text("Allow Location Access")
                    .font(.title2.bold())

                Text("ParkEye uses your location to recommend the nearest available parking lots.")
                    .font(.body)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
            }

            Spacer()

            VStack(spacing: 12) {
                Button {
                    locationService.requestWhenInUseAuthorization()
                } label: {
                    Text("Allow Location Access")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)

                Button {
                    onComplete()
                } label: {
                    Text("Skip")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
            }
            .padding(.horizontal, 32)
            .padding(.bottom, 40)
        }
        .onChange(of: locationService.authorizationStatus) { _, status in
            if status == .authorizedWhenInUse || status == .authorizedAlways {
                onComplete()
            }
        }
    }
}
