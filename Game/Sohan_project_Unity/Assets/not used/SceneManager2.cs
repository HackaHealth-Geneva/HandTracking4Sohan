using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class SceneManager2 : MonoBehaviour
{

    void Start()
    {
        Debug.Log("Start SceneManager 1 ");
        StartCoroutine(WaitAndNextCoroutine());

    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            GameManager.Instance.QuitGame();
         }
    }


    IEnumerator WaitAndNextCoroutine()
    {
        //yield on a new YieldInstruction that waits for 5 seconds.
        yield return new WaitForSeconds(5);
        //SceneManager.LoadScene(0);
        GameManager.Instance.NextScene();
        DestroyAllGameObjects();


    }
    // Start is called before the first frame update





    public void DestroyAllGameObjects()
    {
 
        GameObject[] GameObjects = (FindObjectsOfType<GameObject>() as GameObject[]);

        for (int i = 0; i < GameObjects.Length; i++)
        {
            Destroy(GameObjects[i]);
        }
    }


}
