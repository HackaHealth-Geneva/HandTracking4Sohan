using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro; 

public class SceneManager1 : MonoBehaviour
{

    static int SceneNumber;
    public GameObject cursorGO;
    public GameObject Textbox;

    static int countPlays=0;



    // Start is called before the first frame update
    void Start()
    {
        ///cursorGO.GetComponent<ManagerCursor>().onSelectedItem += WinnerSelectedGO;

        Debug.Log("Start SceneManager 1 ");

        cursorGO = GameObject.Find("Cursor");
        Textbox = GameObject.Find("Canvas/TextBox");

        GameManager.Instance.InstantiateTarget();
        GameManager.Instance.PlayGoToTarget();
        cursorGO.SetActive(false);
        Cursor.visible = false;

        //TextBox appears
        Textbox.GetComponent<Animator>().SetBool("AppearText", true);
        Textbox.GetComponent<AudioSource>().Play(); 
        Textbox.GetComponentInChildren<TMP_Text>().SetText("Trouvez moi! ") ;
     
        StartCoroutine(WaitAndContinueInstantiation());



    }
    IEnumerator WaitAndContinueInstantiation()
    {

        //yield on a new YieldInstruction that waits for 5 seconds.
        yield return new WaitForSeconds(4);


        Textbox.SetActive(false); 


        GameManager.Instance.InstantiateNoTarget();

        //Ask for instantiation and placement of Characters
        GameManager.Instance.CreateAndPlace();
        cursorGO.SetActive(true);


    }


    //private void WinnerSelectedGO(int id)
    //{
    //    GameManager.Instance.ChangeScene(1);
    //    countPlays++;
    //}


    // Update is called once per frame
    void Update()
    {

         if (Input.GetKeyDown(KeyCode.Escape))
        {
            GameManager.Instance.QuitGame();
        }


        if (Input.GetKeyDown(KeyCode.Space))
        {
            Debug.Log("Space KEY DOWN");
            GameManager.Instance.NextScene();
        }

    }


   



   
}
