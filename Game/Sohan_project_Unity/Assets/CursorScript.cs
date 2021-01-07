using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System; 

public class CursorScript : MonoBehaviour
{

 



    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        CursorPosToWorldPos();

    }
    void CursorPosToWorldPos()
    {
        Vector3 mousePos = Input.mousePosition;
        mousePos.z = 0;
        Vector3 worldPosition = Camera.main.ScreenToWorldPoint(mousePos);
        transform.position = new Vector3(worldPosition.x, worldPosition.y, 0);

    }

    void OnCollisionStay2D(Collision2D col)
    {

        Debug.Log("OnCollisionEnter2D " + col.gameObject.tag);

        if (col.gameObject.tag == "Target")
        {

            GameManager.Instance.ObjectSelectedRight(col.gameObject);

        }
        else
        {

            GameManager.Instance.ObjectSelectedWrong(col.gameObject);

        }


    }


}
