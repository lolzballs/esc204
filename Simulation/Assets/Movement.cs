using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Movement : MonoBehaviour
{
    [Header("Joints")]
    public Transform JointA;
    public Transform JointB;
    public Transform JointC;

    [Header("Links")]
    public Transform LinkA;
    public Transform LinkB;
    public Transform LinkC;

    [Header("Link Lengths")]
    public float LinkLengthA;
    public float LinkLengthB;
    public float LinkLengthC;

    private float StartTime;
    private float AnimTime;
    private Vector3 StartPos;
    private Vector3 FinalPos;

    // Start is called before the first frame update
    void Start()
    {
        StartPos = new Vector3(0f, 0.5f, 0);
        FinalPos = new Vector3(0f, 0.5f, 0);
        AnimTime = 0.1f;
        StartTime = Time.fixedTime;

        SetLength(JointB, LinkA, LinkLengthA);
        SetLength(JointC, LinkB, LinkLengthB);
        SetLength(null, LinkC, LinkLengthC);
    }

    // Update is called once per frame
    void Update()
    {
        if (Time.fixedTime > StartTime + AnimTime) {
            return;
        }

        var pos = (FinalPos - StartPos) * (Time.fixedTime - StartTime) / AnimTime + StartPos;
        SetPosition(pos);
    }

    void SetLength(Transform joint, Transform link, float length)
    {
        link.localPosition = new Vector3(0f, 0f, length / 2);
        link.localScale = new Vector3(0.1f, length / 2, 0.1f);

        if (joint != null)
            joint.localPosition = new Vector3(0f, 0f, length);
    }

    public void AnimateTo(Vector3 end, float time)
    {
        StartPos = this.FinalPos;
        FinalPos = end;
        StartTime = Time.fixedTime;
        AnimTime = time;
    }

    public void SetPosition(Vector3 pos, bool intermediate = true)
    {
        bool rightHanded = pos.x < 0;
        var solution = SolveSystem(pos, rightHanded);

        JointA.localEulerAngles = new Vector3(0, solution.x * Mathf.Rad2Deg, 0);
        JointB.localEulerAngles = new Vector3(0, solution.y * Mathf.Rad2Deg, 0);
        JointC.localEulerAngles = new Vector3(0, solution.z * Mathf.Rad2Deg, 0);

        if (!intermediate) {
            FinalPos = pos;
        }
    }

    Vector3 SolveSystem(Vector3 desired, bool rightHanded = false)
    {
        Vector3 solution = new Vector3();

        float phi = desired.z;
        float xb = desired.x - LinkLengthC * Mathf.Cos(phi);
        float yb = desired.y - LinkLengthC * Mathf.Sin(phi);
        float gamma2 = xb * xb + yb * yb;
        float gamma = Mathf.Sqrt(xb * xb + yb * yb);

        float alpha = Mathf.Atan2(yb, xb);
        float beta = Mathf.Acos((LinkLengthA * LinkLengthA + LinkLengthB * LinkLengthB - gamma2) / (2 * LinkLengthA * LinkLengthB));

        float c = 
            Mathf.Acos((gamma2 + LinkLengthA * LinkLengthA - LinkLengthB * LinkLengthB) / (2 * gamma * LinkLengthA));

        solution.y = Mathf.PI - beta;
        solution.x = alpha - c;
        solution.z = phi - solution.x - solution.y;

        if (rightHanded)
        {
            solution.x = solution.x + 2 * c;
            solution.y = -solution.y;
            solution.z = phi - solution.x - solution.y;
        }

        return solution;
    }
}
