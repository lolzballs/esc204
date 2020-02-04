using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraChange : MonoBehaviour
{
    public Camera[] cameras;
    private int currentCamera;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetButtonDown("cameraNext")) {
            NextCamera();
        }
        if (Input.GetButtonDown("cameraPrev")) {
            PrevCamera();
        }
    }

    private void NextCamera() {
        cameras[currentCamera].enabled = false;
        if (currentCamera == cameras.Length - 1) {
            currentCamera = 0;
        } else {
            currentCamera += 1;
        }
        cameras[currentCamera].enabled = true;
    }

    private void PrevCamera() {
        cameras[currentCamera].enabled = false;
        if (currentCamera == 0) {
            currentCamera = cameras.Length - 1;
        } else {
            currentCamera -= 1;
        }
        cameras[currentCamera].enabled = true;
    }
}
