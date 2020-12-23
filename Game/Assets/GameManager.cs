using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;


public class GameManager : MonoBehaviour
{

    static int SceneNumber;
    public GameObject cursorGO;

    static int countPlays=0;



    // Start is called before the first frame update
    void Start()
    {
        cursorGO.GetComponent<ManagerCursor>().onSelectedItem += WinnerSelectedGO;

        Debug.Log("Count Plays" + countPlays); 
    }



  


    private void WinnerSelectedGO(int id)
    {
        ChangeScene(1);
        countPlays++;
    }


    // Update is called once per frame
     void Update()
    {
  

        if (Input.GetKeyDown(KeyCode.Escape))
        {
            QuitGame();
        }
    }


    public void QuitGame()
    {
        // save any game data here
        #if UNITY_EDITOR
                // Application.Quit() does not work in the editor so
                // UnityEditor.EditorApplication.isPlaying need to be set to false to end the game
                UnityEditor.EditorApplication.isPlaying = false;
        #else
                 Application.Quit();
        #endif
    }



    void ChangeScene(int scenenumber)
    {
        SceneManager.LoadScene(scenenumber);
        SceneNumber = scenenumber;
    }
}
