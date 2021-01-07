using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Collision : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    // called when the cube hits the floor
    void OnCollisionStay2D(Collision2D col)
    {
        
        Debug.Log("OnCollisionEnter2D " + col.otherCollider.tag);
    }
}
