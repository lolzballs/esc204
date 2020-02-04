using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RayCast : MonoBehaviour
{
    public GameObject pointer;

    private Camera camera;
    private Transform armTransform;
    private Movement arm;

    void Start()
    {
        camera = this.gameObject.GetComponent<Camera>();
        armTransform = GameObject.Find("Arm").transform;
        
        arm = GameObject.Find("Arm").GetComponent<Movement>();
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetMouseButtonDown(0) && camera.enabled) {
            RaycastHit hit;
            Ray ray = camera.ScreenPointToRay(Input.mousePosition);
            if (Physics.Raycast(ray, out hit)) {
                pointer.transform.position = hit.point;
                pointer.SetActive(true);

                var target = armTransform.InverseTransformPoint(hit.point);
                arm.AnimateTo(new Vector3(target.z, target.x, Random.value * Mathf.PI / 2.0f + Mathf.PI / 4), 1f);
            }
        }

        if (Input.GetKeyDown(KeyCode.R)) {
            arm.SetPosition(new Vector3(-0.5f, 0.10f, Mathf.PI / 2), false);
            arm.AnimateTo(new Vector3(0.5f, 0.10f, Mathf.PI / 2), 10f);
        } else if (Input.GetKeyDown(KeyCode.W)) {
            arm.AnimateTo(new Vector3(0.5f, 0.10f, Mathf.PI / 2), 10f);
        }
    }
}
