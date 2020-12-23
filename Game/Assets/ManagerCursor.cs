using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ManagerCursor : MonoBehaviour
{
    public GameObject cursor;
    public GameObject[] targets; 
    Vector3 worldPosition;
    public GameObject GOSelected;

    public event Action<int> onSelectedItem;

    public Vector3 position1;
    public Vector3 position2;

    // Start is called before the first frame update
    void Start()
    {
        //Set Cursor to not be visible
        Cursor.visible = false;


        //Load Prefabs as GameObjects
        GameObject[] allMaps = Resources.LoadAll<GameObject>("Prefabs");
        //Generate 2 random numbers that will be the indexes of the selected GOs
        Tuple<int, int> indexes = Generate2Randoms(allMaps.Length - 1);


        targets = new GameObject[2];

        //Instantiate the GOs  //Place them in the right position
        position1 = new Vector3(-6,6,0);
        position2 = new Vector3(6,6,0);
        targets[0]= Instantiate(allMaps[indexes.Item1], position1, Quaternion.identity);
        targets[1]= Instantiate(allMaps[indexes.Item2], position2, Quaternion.identity);

        targets[0].AddComponent<Target>();
        targets[1].AddComponent<Target>();

        targets[0].gameObject.tag = "Target";
        targets[1].gameObject.tag = "Target";

        Debug.Log("targets -->" + targets); 


    }



    public Tuple<int, int> Generate2Randoms(int len)
    {
        int a;
        int b;
        a = UnityEngine.Random.Range(0, len);
        b = UnityEngine.Random.Range(0, len);
        while (a == b)
        {
            b = UnityEngine.Random.Range(0, len);
        }
        Tuple<int, int> tupleout = new Tuple<int, int>(a, b);
        Debug.Log("a  " + a + "b " + b);
        return tupleout;
    }



    // Update is called once per frame
    void Update()
    {
        if (Input.anyKeyDown)
        {
            CheckInputButtons();

        }
        else
        {
            CursorPosToWorldPos();
            CheckCursorPosition();
        }

    }


    void CursorPosToWorldPos()
    {
        Vector3 mousePos = Input.mousePosition;
        mousePos.z = 0;
        worldPosition = Camera.main.ScreenToWorldPoint(mousePos);
        cursor.transform.position = new Vector3(worldPosition.x, worldPosition.y, 0);

    }


    void CheckInputButtons()
    {
        if (Input.GetKey("up"))
        {
          
        }

        if (Input.GetKey("down"))
        {
            //cursor.transform.position -= Vector3.up * Time.deltaTime;

        }
        if (Input.GetKey("left"))
        {
            //cursor.transform.position -= Vector3.right * Time.deltaTime;

            //Debug.Log("bravooo!! " + targetgo);
            GOSelected = targets[0];
            DontDestroyOnLoad(GOSelected);
            GOSelected.transform.position = new Vector3(0, 0, 0);
            //GOSelected.transform.localScale = new Vector3(1.5f, 1.5f, 1.5f);
            onSelectedItem(1);
            //Debug.Log("targetgo.GetInstanceID()" + targetgo.GetInstanceID());



        }

        if (Input.GetKey("right"))
        {
            //cursor.transform.position += Vector3.right * Time.deltaTime;

            GOSelected = targets[1];
            DontDestroyOnLoad(GOSelected);
            GOSelected.transform.position = new Vector3(0, 0, 0);
            //GOSelected.transform.localScale = new Vector3(1.5f, 1.5f, 1.5f);
            onSelectedItem(1);

        }
    }

    void CheckCursorPosition()
    {
        foreach (GameObject targetgo in targets)
        {
            if ((targetgo.transform.position - cursor.transform.position).magnitude < 3.0f)
            {

                targetgo.GetComponent<Target>().Inside();
                if (targetgo.GetComponent<Target>().currentState == Target.State.Commited)
                {
                    //Debug.Log("bravooo!! " + targetgo);
                    GOSelected = targetgo;

                    DontDestroyOnLoad(GOSelected);
                    GOSelected.transform.position = new Vector3(0, 0, 0);
                    //GOSelected.transform.localScale = new Vector3(1.5f, 1.5f, 1.5f);
                    
                    onSelectedItem(1);
                    //Debug.Log("targetgo.GetInstanceID()" + targetgo.GetInstanceID());
                }
            }
            else
            {
                if (targetgo.GetComponent<Target>().currentState != Target.State.Unselected)
                {
                    targetgo.GetComponent<Target>().Outside();
                }
            }
        }
    }



    




}
