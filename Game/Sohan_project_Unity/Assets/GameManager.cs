//Created by Sixto Alcoba sixtoalcobabanqueri@gmail.com

using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;
using System.Linq;

public class GameManager : MonoBehaviour
{

    //difficulty level will increment when we have a good result. 
    public static int difficultyLevel;

    //Game Object that the player has to select to win.
    GameObject TargetGO;
    int indextarget;

    //Game Object that the player has to select to win.
    public static GameObject SelectedGO;

    //Game Object that the player has to select to win.
    List<GameObject> TargetsNoGO;

    //DataBase of all animal objects
    static GameObject[] GOAnimalDataBase;

    //number of characters in Game
    int numCharacters = 2;

    
    public static int SceneNumber;

    public static int NumberOfplays = 0;


    static GameObject MusicPlayer; 


    #region SINGLETON
    //Define the instance of this specific class .
    //Need to be static, so it will be running the same instance during the whole execution.
    private static GameManager _instance;
    //this is the instance that will be used for communication with the other Components.
    //Other components can communicate with this GameManager using "GameManager.Instance.METHOD(..."
    public static GameManager Instance
    {
        get
        {

            if (_instance == null)
            {
                //If it doesn't exist, and it has been called by another component,  we create it. 
                //Lazy instantiation: It will create the instance on the fly automatically.
                GameObject goManager = new GameObject("GameManager");
                _instance = goManager.AddComponent<GameManager>();
            }


            return _instance;
        }
    }



    private void Awake()
    {
        //At the begining of all the execution it will assign this specific object to the private instance.
        _instance = this;
        Initialization();

        if(MusicPlayer ==null)
        { 
            MusicPlayer = GameObject.FindGameObjectWithTag("music");
            MusicPlayer.GetComponent<AudioSource>().Play(); 
            DontDestroyOnLoad(MusicPlayer);
        }
    }

    #endregion

    void Initialization()
    {

        //CreateDataBase of Characters
        if (NumberOfplays == 0)
        {
            CreateGOAnimalDataBase();
            //initialize list of characters
            SceneNumber = 0;
        }
        NumberOfplays++;
    }


    


public void CreateGOAnimalDataBase()
    {
        Debug.Log("Creating animal Database");

        GOAnimalDataBase = Resources.LoadAll<GameObject>("Prefabs");
        Debug.Log("GOAnimalDataBase length" + GOAnimalDataBase.Length);
    }



    public void ObjectSelectedWrong(GameObject ObjectSelected)
    {

        SelectedGO = ObjectSelected;
        DontDestroyOnLoad(SelectedGO);
        SceneManager.LoadScene("WrongChoice");

    }

    public void ObjectSelectedRight(GameObject ObjectSelected)
    {
        SelectedGO = ObjectSelected;
        DontDestroyOnLoad(SelectedGO);

        SceneManager.LoadScene("RightChoice");

    }


    public void LoadInitialScene()
    {
        Destroy(SelectedGO);
        SceneManager.LoadScene("Initial");
    }


    public void CreateAndPlace()
    {
        //InstantiateTarget();
        //InstantiateNoTarget();

        TargetGO.GetComponent<Animator>().SetBool("ToCalling", true);
        TargetGO.GetComponent<Animator>().SetBool("ToWin", false);
        TargetGO.GetComponent<Animator>().SetBool("ToIdle", false);

        Debug.Log("ToCalling, true");

        List<Vector3> listPositions=arrangePositionsOfCharacters(numCharacters);
        PlaceCharacters(listPositions);
    }


    public void PlayGoToTarget()
    {


        TargetGO.transform.position = new Vector3(0, 6, 0);

        TargetGO.GetComponent<Animator>().SetBool("ToWin", true);
        TargetGO.GetComponent<Animator>().SetBool("ToCalling", false);
        TargetGO.GetComponent<Animator>().SetBool("ToIdle", false);

        Debug.Log("PlayGoToTarget()");



    }


    public void  InstantiateTarget()
    {
         indextarget = UnityEngine.Random.Range(0, GOAnimalDataBase.Length - 1);
        TargetGO = GOAnimalDataBase[indextarget];
        //TargetGO.AddComponent<Target>();
  
        //TargetGO.AddComponent<BoxCollider2D>();
      
        TargetGO.AddComponent<Rigidbody2D>();
        TargetGO.tag = "Target";
        TargetGO.GetComponent<Rigidbody2D>().constraints = RigidbodyConstraints2D.FreezeAll;


     

        TargetGO= Instantiate( TargetGO, new Vector3(0, 0, 0), Quaternion.identity);
         
 
    }


    //Instantiate Target GO and Non Target GOs
    public void InstantiateNoTarget()
    {
        

        TargetsNoGO = new List<GameObject>();
        //We create as many extra characters as numCharacters-1(TargetGO)
        for (int i = 0; i < numCharacters - 1; i++)
        {
            int indexNoTarget = UnityEngine.Random.Range(0, GOAnimalDataBase.Length);
            while (indexNoTarget == indextarget)
            {
                indexNoTarget = UnityEngine.Random.Range(0, GOAnimalDataBase.Length );
            } 
           // GOAnimalDataBase[indexNoTarget].AddComponent<Target>();
           // GOAnimalDataBase[indexNoTarget].AddComponent<BoxCollider2D>();
            GOAnimalDataBase[indexNoTarget].AddComponent<Rigidbody2D>();
            GOAnimalDataBase[indexNoTarget].tag="NoTarget";
            GOAnimalDataBase[indexNoTarget].GetComponent<Rigidbody2D>().constraints = RigidbodyConstraints2D.FreezeAll;

            GOAnimalDataBase[indexNoTarget].GetComponent<Animator>().SetBool("ToWin", false);
            GOAnimalDataBase[indexNoTarget].GetComponent<Animator>().SetBool("ToCalling", false);
            GOAnimalDataBase[indexNoTarget].GetComponent<Animator>().SetBool("ToIdle", true);

            TargetsNoGO.Add(GOAnimalDataBase[indexNoTarget]);

        }
    }

    //Depending the number of character we will place the objects in specific positions
    //This function will give a List with the number of positions
    List<Vector3> arrangePositionsOfCharacters(int numberCharacters)
    {
        List<Vector3> positionsOut = new List<Vector3>();
        //populate list
        switch (numberCharacters)
        {
            case 2:
                //Horizontal or Vertical selected randomly: 
                int random = UnityEngine.Random.Range(0, 1);
                if (random == 0)
                {
                    //Horizontal
                    positionsOut.Add(new Vector3(-5.5f, 6, 0));
                    positionsOut.Add(new Vector3(5.5f, 6, 0));
                }
                else
                {
                    //vertical
                    positionsOut.Add(new Vector3(5.5f, -6, 0));
                    positionsOut.Add(new Vector3(5.5f, 6, 0));
                }
                break;

            case 3:
                //TO DO 
                break;
            case 4:
                //TO DO 
                break;
        }
        return positionsOut;

    }

     void PlaceCharacters(List<Vector3> listpositions )
    {
        //Place TargetGO 
        TargetGO.transform.position = listpositions[0];
        Debug.Log("POSITION WHERE TARGET SHOULD BE : " + TargetGO.transform.position);
        listpositions.RemoveAt(0);

        if(listpositions.Count != TargetsNoGO.Count)
        {
            Debug.LogError("listpositions.Count != TargetsNoGO.Count"); 
        }
        else
        {
            for(int i=0; i<listpositions.Count;i++)
            {

                Instantiate(TargetsNoGO.ElementAt(i), listpositions[i], Quaternion.identity);
            }

        }
        
    }


    //Depending the difficulty level we will place a different number of character
    int NumberofCharacters(int difficultyLevel)
    {
        int charactersout = 0;
        if (difficultyLevel < 10)
        {
            //2 characters
            return 2;
        }
        else if (difficultyLevel < 20)
        {
            //3 characters
            return 3;
        }
        else
        {
            //4 characters
            return 4;
        }
    }

    // Start is called before the first frame update
    void Start()
    {
        Debug.Log("Start Game Manager SceneNumber "+ SceneNumber);
        Debug.Log( "difficulty level " + difficultyLevel + "Number of characters  " + NumberofCharacters(difficultyLevel));
        TargetsNoGO = new List<GameObject>();

    }

    // Update is called once per frame
    void Update()
    {
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

    public void NextScene()
    {
        Debug.Log("NExt Scene SceneNumber before" + SceneNumber);
        
        //When SceneNumber is the last one we start from 0
        if (SceneNumber == 1)
        {
            Debug.Log("SceneNumber is 1!!");

           SceneNumber = 0;
            //TO CHANGE ONLY FOR DEBUG
           difficultyLevel++;
        }
        else 
        { 
            SceneNumber++;
       
        }
        Debug.Log("NExt Scene SceneNumber" + SceneNumber); 
        SceneManager.LoadScene(SceneNumber);
    }

}
