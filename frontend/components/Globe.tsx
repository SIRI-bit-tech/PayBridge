"use client"

import { useEffect, useRef } from "react"
import * as THREE from "three"

type GlobeProps = {
  className?: string
  /**
   * Width/height ratio preserved; height adapts with container.
   */
  rotationSpeed?: number
  height?: number
}

export function Globe({ className, rotationSpeed = 0.003, height = 460 }: GlobeProps) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null)
  const frameRef = useRef<number | null>(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const scene = new THREE.Scene()

    // Subtle starfield background
    const starGeometry = new THREE.BufferGeometry()
    const starCount = 800
    const positions = new Float32Array(starCount * 3)
    for (let i = 0; i < starCount * 3; i++) {
      positions[i] = (Math.random() - 0.5) * 2000
    }
    starGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3))
    const starMaterial = new THREE.PointsMaterial({ color: 0xffffff, size: 1 })
    const stars = new THREE.Points(starGeometry, starMaterial)
    scene.add(stars)

    const camera = new THREE.PerspectiveCamera(
      45,
      container.clientWidth / container.clientHeight,
      0.1,
      2000
    )
    camera.position.set(0, 0, 6)

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setSize(container.clientWidth, container.clientHeight)
    container.appendChild(renderer.domElement)
    rendererRef.current = renderer

    // Lighting
    scene.add(new THREE.AmbientLight(0xffffff, 0.4))
    const dirLight = new THREE.DirectionalLight(0xffffff, 1)
    dirLight.position.set(5, 3, 5)
    scene.add(dirLight)

    // Earth
    const sphere = new THREE.SphereGeometry(2, 64, 64)
    const loader = new THREE.TextureLoader()
    // Public textures from three.js examples (reasonably sized)
    const earthMapUrl = "https://threejs.org/examples/textures/land_ocean_ice_cloud_2048.jpg"
    const earthBumpUrl = "https://threejs.org/examples/textures/planets/earth_bump.jpg"
    const earthSpecUrl = "https://threejs.org/examples/textures/planets/earth_specular_2048.jpg"

    const [colorMap, bumpMap, specMap] = [
      loader.load(earthMapUrl),
      loader.load(earthBumpUrl),
      loader.load(earthSpecUrl),
    ]

    const material = new THREE.MeshPhongMaterial({
      map: colorMap,
      bumpMap: bumpMap,
      bumpScale: 0.05,
      specularMap: specMap,
      specular: new THREE.Color("#222222"),
      shininess: 10,
    })
    const earth = new THREE.Mesh(sphere, material)

    // Face Africa roughly towards the camera (≈ 20°E)
    earth.rotation.y = -THREE.MathUtils.degToRad(20)
    scene.add(earth)

    const onResize = () => {
      if (!container || !rendererRef.current) return
      const { clientWidth, clientHeight } = container
      camera.aspect = clientWidth / clientHeight
      camera.updateProjectionMatrix()
      rendererRef.current.setSize(clientWidth, clientHeight)
    }
    const observer = new ResizeObserver(onResize)
    observer.observe(container)

    const animate = () => {
      earth.rotation.y += rotationSpeed
      frameRef.current = requestAnimationFrame(animate)
      renderer.render(scene, camera)
    }
    frameRef.current = requestAnimationFrame(animate)

    return () => {
      if (frameRef.current !== null) cancelAnimationFrame(frameRef.current)
      observer.disconnect()
      scene.clear()
      renderer.dispose()
      container.removeChild(renderer.domElement)
      rendererRef.current = null
    }
  }, [rotationSpeed])

  return (
    <div
      ref={containerRef}
      className={className}
      style={{ width: "100%", height: `${height}px` }}
    />
  )
}

export default Globe


