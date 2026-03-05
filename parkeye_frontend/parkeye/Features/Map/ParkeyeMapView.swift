import MapKit
import SwiftUI

struct ParkeyeMapView: UIViewRepresentable {
    var viewModel: MapViewModel

    private static let gmuCenter = CLLocationCoordinate2D(latitude: 38.8316, longitude: -77.3076)
    private static let gmuSpan = MKCoordinateSpan(latitudeDelta: 0.025, longitudeDelta: 0.025)

    func makeCoordinator() -> Coordinator {
        Coordinator(viewModel: viewModel)
    }

    func makeUIView(context: Context) -> MKMapView {
        let mapView = MKMapView()
        mapView.delegate = context.coordinator
        mapView.setRegion(
            MKCoordinateRegion(center: Self.gmuCenter, span: Self.gmuSpan),
            animated: false
        )
        context.coordinator.loadOverlays(on: mapView)

        let tap = UITapGestureRecognizer(target: context.coordinator,
                                         action: #selector(Coordinator.handleMapTap(_:)))
        tap.delegate = context.coordinator
        mapView.addGestureRecognizer(tap)

        return mapView
    }

    func updateUIView(_ mapView: MKMapView, context: Context) {
        context.coordinator.viewModel = viewModel
        context.coordinator.updateColors()
    }

    // MARK: - Coordinator

    class Coordinator: NSObject, MKMapViewDelegate, UIGestureRecognizerDelegate {
        var viewModel: MapViewModel
        private var rendererCache: [String: LotPolygonRenderer] = [:]
        private weak var mapView: MKMapView?

        init(viewModel: MapViewModel) {
            self.viewModel = viewModel
        }

        func loadOverlays(on mapView: MKMapView) {
            self.mapView = mapView
            guard
                let url = Bundle.main.url(forResource: "LotData", withExtension: "geojson"),
                let data = try? Data(contentsOf: url),
                let features = try? MKGeoJSONDecoder().decode(data)
            else { return }

            for feature in features.compactMap({ $0 as? MKGeoJSONFeature }) {
                guard let id = feature.identifier else { continue }
                for polygon in feature.geometry.compactMap({ $0 as? MKPolygon }) {
                    polygon.subtitle = id
                    mapView.addOverlay(polygon, level: .aboveRoads)
                }
            }
        }

        func updateColors() {
            for (id, renderer) in rendererCache {
                let hex = lot(for: id)?.color ?? "808080"
                renderer.updateColor(hexColor: hex)
            }
        }

        private func lot(for id: String) -> Lot? {
            viewModel.lots.first { $0.id.uuidString.lowercased() == id.lowercased() }
        }

        // MARK: Tap handling

        @objc func handleMapTap(_ gesture: UITapGestureRecognizer) {
            guard let mapView, gesture.state == .ended else { return }
            let point = gesture.location(in: mapView)
            let coord = mapView.convert(point, toCoordinateFrom: mapView)
            let mapPoint = MKMapPoint(coord)

            for overlay in mapView.overlays {
                guard let polygon = overlay as? MKPolygon,
                      let idString = polygon.subtitle,
                      let uuid = UUID(uuidString: idString),
                      let renderer = mapView.renderer(for: polygon) as? MKPolygonRenderer else { continue }
                let polyPoint = renderer.point(for: mapPoint)
                if renderer.path?.contains(polyPoint) == true {
                    viewModel.selectLot(id: uuid)
                    return
                }
            }
        }

        // Allow simultaneous recognition with map's built-in gestures
        func gestureRecognizer(_ gestureRecognizer: UIGestureRecognizer,
                               shouldRecognizeSimultaneouslyWith other: UIGestureRecognizer) -> Bool {
            true
        }

        // MARK: MKMapViewDelegate

        func mapView(_ mapView: MKMapView, rendererFor overlay: MKOverlay) -> MKOverlayRenderer {
            guard let polygon = overlay as? MKPolygon, let id = polygon.subtitle else {
                return MKOverlayRenderer(overlay: overlay)
            }
            let renderer = LotPolygonRenderer(polygon: polygon)
            renderer.configure(hexColor: lot(for: id)?.color ?? "808080")
            rendererCache[id] = renderer
            return renderer
        }
    }
}
